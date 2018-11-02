from flask import Flask, Response, request
import os
import json
import logging
from kafka import KafkaConsumer, TopicPartition
from since_codec import encode_since, decode_since
from entity_json import entities_to_json

app = Flask(__name__)

logger = logging.getLogger('service')
logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))

config = json.loads(os.environ["CONFIG"])

consumer_timeout_ms = config.get("consumer_timeout_ms", 60000)


@app.route('/', methods=["GET"])
def get():
    if config.get("sasl_username"):
        import ssl
        context = ssl.create_default_context()
        consumer = KafkaConsumer(bootstrap_servers=config["bootstrap_servers"],
                                 consumer_timeout_ms=consumer_timeout_ms,
                                 enable_auto_commit=False,
                                 security_protocol="SASL_SSL",
                                 ssl_context=context,
                                 sasl_mechanism="PLAIN",
                                 sasl_plain_username=config["sasl_username"],
                                 sasl_plain_password=config["sasl_password"])
    else:
        consumer = KafkaConsumer(bootstrap_servers=config["bootstrap_servers"],
                                 consumer_timeout_ms=consumer_timeout_ms,
                                 enable_auto_commit=False)

    topic = config["topic"]
    if config.get("partitions"):
        partitions = config.get("partitions")
    else:
        partitions = consumer.partitions_for_topic(topic)

    consumer.assign([TopicPartition(topic, partition) for partition in partitions])

    since = request.args.get("since")
    if since:
        offsets = decode_since(partitions, since)
        for partition in partitions:
            offset = offsets.get(partition)
            if offset:
                logger.info("seeking to offset %s for partition %s" % (offset, partition))
                consumer.seek(TopicPartition(topic, partition), offset + 1)

    elif config.get("seek_to_beginning", False):
        offsets = {}
        logger.info("no since, seeking to beginning")
        consumer.seek_to_beginning()
    else:
        offsets = {}
        logger.info("no since, consuming from end")

    limit = request.args.get("limit")

    decode_json_value = config.get("decode_json_value", False)

    def generate():
        yield "["
        index = 0
        for entity in consumer:
            if index > 0:
                yield ","
            offsets[entity.partition] = entity.offset

            result = {
                "_updated": encode_since(partitions, offsets),
                "timestamp": entity.timestamp,
                "offset": entity.offset,
                "partition": entity.partition,
                "value": json.loads(entity.value.decode('utf-8')) if decode_json_value else entity.value,
                "key": entity.key
            }
            if entity.key:
                try:
                    # keys in kafka can be any bytes, but we map to _id string if possible
                    result["_id"] = entity.key.decode("utf-8")
                except UnicodeDecodeError:
                    pass

            yield entities_to_json(result)
            index = index + 1
            if limit and index > int(limit):
                break
        yield "]"
    return Response(generate(), mimetype='application/json', )


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0')

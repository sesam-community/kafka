from flask import Flask, Response, request
import cherrypy
import os
import json
import logging
from kafka import KafkaConsumer, TopicPartition
from since_codec import encode_since, decode_since
from entity_json import entities_to_json
from certificate_handler import CertificateHandler

app = Flask(__name__)

logger = logging.getLogger("kafka-service")
logging.basicConfig(level=os.environ.get("LOG_LEVEL", "INFO"))

auth_method = os.environ.get("AUTH_METHOD")     # credentials or certificate

config = json.loads(os.environ["CONFIG"])       # kafka specific config
consumer_timeout_ms = config.get("consumer_timeout_ms", 60000)
enable_auto_commit = config.get("enable_auto_commit", False)


@app.route("/<path:topic>", methods=["GET"])
def get(topic):

    logger.debug(f"topic: {topic}")

    if auth_method == "credentials":
        logger.info("Authenticating with username/password...")

        import ssl
        context = ssl.create_default_context()

        consumer = KafkaConsumer(bootstrap_servers=config["bootstrap_servers"],
                                 consumer_timeout_ms=consumer_timeout_ms,
                                 enable_auto_commit=enable_auto_commit,
                                 security_protocol="SASL_SSL",
                                 ssl_context=context,
                                 sasl_mechanism="PLAIN",
                                 sasl_plain_username=config["sasl_username"],
                                 sasl_plain_password=config["sasl_password"])

    elif auth_method == "certificate":
        logger.info("Authenticating with certificate...")

        ssl_ca = config["ssl_ca"]
        ssl_cafile = config.get("ssl_cafile", "ca.pem")
        ssl_cert = config["ssl_cert"]
        ssl_certfile = config.get("ssl_certfile", "cert.pem")
        ssl_key = config["ssl_key"]
        ssl_keyfile = config.get("ssl_keyfile", "pkey.pem")

        ca = CertificateHandler(ssl_ca, ssl_cafile)
        cert = CertificateHandler(ssl_cert, ssl_certfile)
        pkey = CertificateHandler(ssl_key, ssl_keyfile)

        logger.debug(ca)
        logger.debug(cert)
        logger.debug(pkey)

        # write certs to disk
        ca.write()
        cert.write()
        pkey.write()

        consumer = KafkaConsumer(bootstrap_servers=config["bootstrap_servers"],
                                 consumer_timeout_ms=consumer_timeout_ms,
                                 enable_auto_commit=enable_auto_commit,
                                 security_protocol="SSL",
                                 ssl_cafile=ssl_cafile,
                                 ssl_certfile=ssl_certfile,
                                 ssl_keyfile=ssl_keyfile)

    else:
        consumer = KafkaConsumer(bootstrap_servers=config["bootstrap_servers"],
                                 consumer_timeout_ms=consumer_timeout_ms,
                                 enable_auto_commit=enable_auto_commit)

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
                logger.info(f"seeking to offset {offset} for partition {partition}")
                consumer.seek(TopicPartition(topic, partition), offset + 1)

    elif config.get("seek_to_beginning", True):
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

            # identify content type to determine how to transform into JSON
            content_type = next((v[1] for i, v in enumerate(entity.headers) if v[0] == "Content-Type"), None).decode("utf-8")
            result = {
                "_updated": encode_since(partitions, offsets),
                "timestamp": entity.timestamp,
                "offset": entity.offset,
                "partition": entity.partition,
                "content-type": "application/json" if decode_json_value else content_type,
                "value": json.loads(entity.value.decode("utf-8")) if decode_json_value else entity.value,
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
    return Response(generate(), mimetype="application/json", )


if __name__ == "__main__":
    cherrypy.tree.graft(app, "/")

    # Set the configuration of the web server to production mode
    cherrypy.config.update({
        "environment": "production",
        "engine.autoreload_on": False,
        "log.screen": True,
        "server.socket_port": 5000,
        "server.socket_host": "0.0.0.0"
    })

    # Start the CherryPy WSGI web server
    cherrypy.engine.start()
    cherrypy.engine.block()

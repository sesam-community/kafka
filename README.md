# Read Kafka events as a json source

Example system config:
```
{
  "_id": "eventhubs-trafikkdata",
  "type": "system:microservice",
  "docker": {
    "environment": {
      "CONFIG": {
        "bootstrap_servers": "svv-poc.servicebus.windows.net:9093",
        "consumer_timeout_ms": 5000,
        "decode_json_value": true,
        "partitions": [0, 1, 2, 3],
        "sasl_password": "[...]",
        "sasl_username": "$ConnectionString",
        "seek_to_beginning": true,
        "topic": "trafikkdata"
      }
    },
    "image": "sesamcommunity/kafka",
    "port": 5000
  }
}

```

Example source pipe:
```
{
  "source": {
    "type": "json",
    "system": "eventhubs-trafikkdata",
    "is_chronological": true,
    "supports_since": true,
    "url": "/"
  }
}

```

## Limitations

* One microservice pr consumer/topic
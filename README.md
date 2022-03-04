# Kafka source connector

Kafka microservice connector for streaming Kafka topics as JSON.

Supports:
- Credential authentication
- Certificate authentication
- One pipe for each topic

Kafka-python KafkaConsumer: https://kafka-python.readthedocs.io/en/master/apidoc/KafkaConsumer.html

## Environment variables

`AUTH_METHOD` - Authentication method ("credentials" or "certificate")

`CONFIG.bootstrap_servers` - Comma separated string of Kafka bootstrap servers ("server1:port1,server2:port2,...")

`CONFIG.consumer_timeout_ms` - number of milliseconds to block during message iteration before raising StopIteration (Default: 60000)

`CONFIG.decode_json_value` - Set this to `true` if the `value` property returned from Kafka is JSON (Default: `false`)

`CONFIG.seek_to_beginning` - Set this to `false` to only read new records (Default: `true`) **WARNING!** See Limitations below.

**Note!**

For credential authentication: Kafka uses port *9094* by default.

For certificate authentication: Kafka uses port *9093* by default.

### For AUTH_METHOD = "credentials"

`CONFIG.sasl_username` - Username to authenticate with the Kafka

`CONFIG.sasl_password` - Password to authenticate with the Kafka

### For AUTH_METHOD = "certificate"

`CONFIG.ssl_ca` - CA certificate chain

`CONFIG.ssl_cafile` - File name in which to store `CONFIG.ssl_ca` (Default: `ca.pem`)

`CONFIG.ssl_cert` - Client certificate

`CONFIG.ssl_certfile` - File name in which to store `CONFIG.ssl_cert` (Default: `cert.pem`)

`CONFIG.ssl_key` - Private key

`CONFIG.ssl_keyfile` - File name in which to store `CONFIG.ssl_key` (Default: `pkey.pem`)

## Example system config using credential authentication:
```
{
  "_id": "kafka",
  "type": "system:microservice",
  "docker": {
    "environment": {
      "AUTH_METHOD": "credentials",
      "CONFIG": {
        "bootstrap_servers": "some.kafka.server:9094",
        "decode_json_value": true,
        "partitions": [0, 1, 2, 3],
        "sasl_password": "$SECRET(password)",
        "sasl_username": "$ENV(user)"
      }
    },
    "image": "sesamcommunity/kafka",
    "port": 5000
  }
}

```

## Example system config using certificate authentication:
```
{
  "_id": "kafka",
  "type": "system:microservice",
  "docker": {
    "environment": {
      "AUTH_METHOD": "certificate",
      "CONFIG": {
        "bootstrap_servers": "some.kafka.server:9093",
        "partitions": [0, 1, 2, 3],
        "ssl_ca": "$SECRET(kafka-ca)",
        "ssl_cafile": "/service/server.pem",
        "ssl_cert": "$SECRET(kafka-cert)",
        "ssl_certfile": "/service/cert.pem",
        "ssl_key": "$SECRET(kafka-pkey)",
        "ssl_keyfile": "/service/pkey.pem"
      },
      "LOG_LEVEL": "INFO"
    },
    "image": "sesamcommunity/kafka",
    "port": 5000
  },
  "verify_ssl": true
}

```

## Example source pipe:
```
{
  "_id": "kafka-some-topic",
  "type": "pipe",
  "source": {
    "type": "json",
    "system": "kafka",
    "url": "/some-topic"
  }
}
```

## Limitations

Limited or no since support.

Setting `seek_to_beginning` to `false` may result in loss of data. Use with caution.
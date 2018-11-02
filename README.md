# Read Kafka events into an http_endpoint

Example system config:
```
{
  "_id": "my-kafka-foo-reader",
  "type": "system:microservice",
  "docker": {
    "environment": {
      "CONFIG": {
        [TODO]
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
    "type": "json"
    "url": "/"
  }
  "transform": {
    "type": "dtl",
  }
}
```

## Limitations

* One microservice pr consumer/topic
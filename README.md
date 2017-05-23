# nr_queue_monitoring

you have to defined the following environment variables:
- NEWRELIC_HOSTNAME=exemple
- NEWRELIC_LICENCE_KEY=nr_licence_key
- COUNTER_REDIS_HOST=redis
- COUNTER_REDIS_PORT=6379
- COUNTER_REDIS_DATABASE=1
- COUNTER_REDIS_QUEUE_PREFIX=counter

To launch application run:
```
docker run webgeoservices/nr_queue_monitoring
```

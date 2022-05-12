#!/bin/sh

if [ "$BROKER" = "rabbitmq" ]
then
    echo "Waiting for broker RabbitMQ..."
    while ! nc -z $RABBIT_HOST $RABBIT_PORT; do
      sleep 0.1
    done
    echo "Broker RabbitMQ started"
    echo "Waiting 10 sec before start application..."
    sleep 10
fi

python app/main.py

exec "$@"
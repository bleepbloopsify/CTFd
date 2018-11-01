#!/bin/bash

sudo mkdir /etc/redis
sudo cp ./redis.conf /etc/redis/

sudo adduser --system --group --no-create-home redis
sudo mkdir /var/lib/redis
sudo chown redis:redis /var/lib/redis
sudo chmod 770 /var/lib/redis
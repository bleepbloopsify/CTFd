#!/bin/bash
wget http://download.redis.io/redis-stable.tar.gz
tar xvzf redis-stable.tar.gz
cd redis-stable
make
sudo make install

cd ..
rm -rf redis-stable

sudo mkdir /etc/redis
sudo rm /etc/redis/redis/conf
sudo ln -s  $(pwd)/redis.conf /etc/redis/

sudo adduser --system --group --no-create-home redis
sudo mkdir /var/lib/redis
sudo chown redis:redis -R /var/lib/redis
sudo chmod 770 -R /var/lib/redis

sudo ln -s $(pwd)/ctfd-redis.service /etc/systemd/system/

sudo systemctl start ctfd-redis
sudo systemctl enable ctfd-redis
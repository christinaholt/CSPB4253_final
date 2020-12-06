#!/bin/bash

# Install Python, pip, and git
sudo apt-get update
sudo apt-get install -y python3 python3-pip git

mkdir -p /srv
cd /srv

curl http://metadata/computeMetadata/v1/instance/attributes/credentials -H "Metadata-Flavor: Google" > service-credentials.json

# Install Google clients
pip3 install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
export GOOGLE_CLOUD_PROJECT=$(curl http://metadata/computeMetadata/v1/instance/attributes/project -H "Metadata-Flavor: Google")

# Install flask
git clone https://github.com/pallets/flask

cd /flask/examples/tutorial &&
sudo python3 setup.py install &&
sudo pip3 install -e . &&
export FLASK_APP=flaskr

# Install kubectl
sudo apt-get update && sudo apt-get install -y apt-transport-https gnupg2 curl
curl -s https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -
echo "deb https://apt.kubernetes.io/ kubernetes-xenial main" | sudo tee -a /etc/apt/sources.list.d/kubernetes.list
sudo apt-get update
sudo apt-get install -y kubectl

# Install redis, rabbitmq, kubectl
pip3 install redis, rabbitmq


# My aliases
alias ll='ls -l'


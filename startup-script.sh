#!/bin/bash


#
# Christina Holt
# CSPB 4253, Fall 2020
#
# Script installs flask with pip on instance at startup.
#

# Install Python, pip, and git
sudo apt-get update
sudo apt-get install -y python3 python3-pip git redis rabbitmq
sudo apt-get install -y google-api-python-clien


# Clone the flask project
git clone https://github.com/pallets/flask

# Startup flask
cd /flask/examples/tutorial &&
sudo python3 setup.py install &&
sudo pip3 install -e . &&
export FLASK_APP=flaskr


# Install kubectl, google-api-python-client,

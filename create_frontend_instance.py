#!/usr/bin/env python3

'''
Author: Christina Holt, Fall 2020

Disclaimer: This code is based on original template files provided for Lab 5,
and makes HEAVY use of the examples provided by the GCP Python Interface
tutorial here: https://github.com/GoogleCloudPlatform/python-docs-samples.

This script creates a virtual machine, launches a startup-script that utilizes a
service account to launch a second virtual machine where flask is launched from
a startup script.

'''

import argparse
import os
import time
from pprint import pprint

import googleapiclient.discovery
import google.auth
import google.oauth2.service_account as service_account


def create_instance(compute, project, zone, name):

    # Get the latest Ubuntu Bionic Beaver image
    image_response = compute.images().getFromFamily(
        project='ubuntu-os-cloud', family='ubuntu-1804-lts').execute()
    source_disk_image = image_response['selfLink']

    # Configure the machine
    machine_type = "zones/%s/machineTypes/f1-micro" % zone
    startup_script = open(
        os.path.join(
            os.path.dirname(__file__), 'startup-script.sh'), 'r').read()

    #create_v2_code = open(
    #    os.path.join(
    #        os.path.dirname(__file__), 'create_v2.py'), 'r').read()

    #startup_v2_script = open(
    #    os.path.join(
    #        os.path.dirname(__file__), 'startup-v2-script.sh'), 'r').read()

    credentials = open(
        os.path.join(
            os.path.dirname(__file__), 'service-credentials.json'), 'r').read()

    config = {
        'name': name,
        'machineType': machine_type,

        # Specify the boot disk
        'disks': [
            {
                'boot': True,
                'autoDelete': True,
                'initializeParams': {
                    'sourceImage': source_disk_image,
                }
            }
        ],
        # Specify a network interface with NAT to access the public
        # internet.
        'networkInterfaces': [{
            'network': 'global/networks/default',
            'accessConfigs': [
                {'type': 'ONE_TO_ONE_NAT', 'name': 'External NAT'}
            ]
        }],

        # Allow the instance to access cloud storage and logging.
        'serviceAccounts': [{
            'email': 'default',
            'scopes': [
                'https://www.googleapis.com/auth/devstorage.read_write',
                'https://www.googleapis.com/auth/logging.write'
            ]
        }],

        # Metadata is readable from the instance and allows you to
        # pass configuration from deployment scripts to instances.
        'metadata': {
            'items': [{
                # Startup script is automatically executed by the
                # instance upon startup.
                'key': 'startup-script',
                'value': startup_script
            },
            #{
            #    'key': 'create-vm2-code',
            #    'value': create_v2_code,
            #},
            #{
            #    'key': 'vm2-script',
            #    'value': startup_v2_script,
            #},
            {   'key': 'credentials',
                'value': credentials,
            },
            {   'key': 'project',
                'value': project,
            },
            ]
        }
    }

    return compute.instances().insert(
        project=project,
        zone=zone,
        body=config).execute()


def list_instances(compute, project, zone):
    result = compute.instances().list(project=project, zone=zone).execute()
    return result['items'] if 'items' in result else None

def set_firewall_tags(service, project, zone, instance):

    request = service.instances().get(project=project, zone=zone, instance=instance)
    response = request.execute()
    fingerprint = response['tags']['fingerprint']

    tags_body = {
        'items': [
            'allow-5000',
            'allow-redis',
            'allow-rabbitmq'
        ],
        'fingerprint': fingerprint
    }
    return service.instances().setTags(
        project=project,
        zone=zone,
        instance=instance,
        body=tags_body).execute()

if __name__ == '__main__':

    _, project = google.auth.default()
    credentials = service_account.Credentials.from_service_account_file(filename='service-credentials.json')
    project = os.getenv('GOOGLE_CLOUD_PROJECT') or project

    service = googleapiclient.discovery.build('compute', 'v1', credentials=credentials)

    # Hard-coding for Lab5 use
    zone = 'us-central1-a'
    instance_name = 'crh-final'

    operation = create_instance(service, project, zone, instance_name)

    # Set firewall tag in instance
    tags = set_firewall_tags(service, project, zone, instance_name)

    request = service.instances().get(project=project, zone=zone,
            instance=instance_name)
    response = request.execute()

    pprint(response)
    external_ip = response['networkInterfaces'][0]['accessConfigs'][0]['natIP']
    print(f'The instance has been created. Check it out here: \
            http://{external_ip}:5000')




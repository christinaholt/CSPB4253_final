from flask import Flask, request, Response
from google.cloud import storage
import jsonpickle, pickle
import platform
import io, os, sys
import pika
import redis
import hashlib, requests
from PIL import Image

##
## Configure test vs. production
##
redisHost = os.getenv("REDIS_HOST") or "localhost"
rabbitMQHost = os.getenv("RABBITMQ_HOST") or "localhost"

print("Connecting to rabbitmq({}) and redis({})".format(rabbitMQHost,redisHost))

def getRMQ():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=rabbitMQHost))
    channel = connection.channel()

    channel.queue_delete(queue='toWorker')
    channel.queue_declare(queue='toWorker')
    channel.exchange_declare(exchange='logs', exchange_type='topic')

    return channel

# Set up the functions to log messages. Borrowed from solution from in-class
# video.

infoKey = f'{platform.node()}.rest.info'
debugKey = f'{platform.node()}.rest.debug'

def log_debug(message, channel, key=debugKey):
    print(f'DEBUG: {message}', file=sys.stderr)
    channel.basic_publish(exchange='logs', routing_key=key, body=message)

def log_info(message, channel, key=infoKey):
    print(f'INFO: {message}', file=sys.stderr)
    channel.basic_publish(exchange='logs', routing_key=key, body=message)


# Initialize the Flask application
app = Flask(__name__)


def download_public_file(bucket_name, source_blob_name, destination_file_name):

    '''Downloads a public blob from the bucket.'''

    # bucket_name = "your-bucket-name"
    # source_blob_name = "storage-object-name"
    # destination_file_name = "local/path/to/file"

    storage_client = storage.Client.create_anonymous_client()

    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(source_blob_name)
    blob.download_to_filename(destination_file_name)

    print(
        "Downloaded public blob {} from bucket {} to {}.".format(
            source_blob_name, bucket.name, destination_file_name
        )
    )


@app.route('/plot/map', methods=['POST'])
def plot_map():

    ''' Send a message to Rabbit MQ to plot an image. Information expected in
    data is as follows:

        start    Time the forecast begins (YYYYMMDDHH)
        fcst     The forecast hour to plot (integer)
        field    The forecast field name to plot (str)
        level    The atmospheric level to plot (str)
    '''

    rmq = getRMQ()

    r = request

    data = jsonpickle.decode(r.data)
    status = 200


    # TODO: Look for file in Redis DB to see if it needs to be retrieved.

    # Retrieve the data file

    start = data.get('start')
    fcst = int(data.get('fcst'))
    hrrr_blob = f'hrrr.{start[0:8]}/conus/hrrr.t{start[8:]}z.wrfprsf{fcst:02d}.grib2'
    bucket_name = f'high-resolution-rapid-refresh'
    hrrr_file = f'./grib/{hrrr_blob}'

    os.makedirs(os.path.dirname(hrrr_file), exist_ok=True)

    log_info(f'Downloading {hrrr_file} from GCP bucket {bucket_name} to {hrrr_file}', rmq)
    download_public_file(bucket_name, hrrr_blob, hrrr_file)

    body = {
        'file': hrrr_file,
        'field': data.get('field'),
        'level': data.get('level'),
        }

    log_info(f"Requesting a map for {data.get('field')} at {data.get('level')} on {start} + {fcst} h", rmq)
    # Request worker to plot a field at a level from the retrieved file.
    pickled_body = jsonpickle.encode(body)

    rmq.basic_publish(exchange='', routing_key='toWorker',
        body=pickled_body)

    return Response(pickled_body,
            status=status,
            mimetype='application/json')

# Respond with health message
@app.route('/', methods=['GET'])
def hello():
    return '<h1> Face Rec Server</h1><p> Use a valid endpoint </p>'


# start flask app
app.run(host="0.0.0.0", port=5000)


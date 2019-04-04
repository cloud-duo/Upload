import json
import os
import uuid
from flask import Flask, request
from google.cloud import storage

# If `entrypoint` is not defined in app.yaml, App Engine will look for an app
# called `app` in `main.py`.
app = Flask(__name__)


@app.route('/upload', methods=['POST'])
def upload():
    storage_client = storage.Client.from_service_account_json('keys.json')

    bucket_name = 'galeata_magica_123'

    bucket = storage_client.get_bucket(bucket_name)

    for filename in request.files:
        f = request.files[filename]
        id = str(uuid.uuid4())
        name = id + ".mp4"  # yes
        # f.save(name)
        blob = bucket.blob(name)
        blob.upload_from_file(f)

        return json.dumps({'id': id})


@app.route('/')
def hello():
    """Return a friendly HTTP greeting."""
    return 'this will be the upload!!'


if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)
# [END gae_python37_app]

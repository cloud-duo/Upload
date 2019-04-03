import json
import os
import uuid

import pymysql
import sqlalchemy
from flask import Flask, request
from google.cloud import storage

pymysql.install_as_MySQLdb()
# If `entrypoint` is not defined in app.yaml, App Engine will look for an app
# called `app` in `main.py`.
app = Flask(__name__)

# [START cloud_sql_mysql_sqlalchemy_create]
# The SQLAlchemy engine will help manage interactions, including automatically
# managing a pool of connections to your database
if os.environ.get('GAE_ENV') == 'standard':
    q = {
        'unix_socket': '/cloudsql/{}'.format('upload-236510:europe-west1:lovely-sql'),
    }
else:
    q = {
        'host': '35.241.170.126'
    }

db = sqlalchemy.create_engine(
    # Equivalent URL:
    # mysql+pymysql://<db_user>:<db_pass>@/<db_name>?unix_socket=/cloudsql/<cloud_sql_instance_name>
    sqlalchemy.engine.url.URL(
        drivername='mysql',
        username='admin',
        password='admin',
        database='data',
        query=q
    ),

    pool_size=5,
    max_overflow=2,
    pool_timeout=30,  # 30 seconds
    pool_recycle=1800,  # 30 minutes
)


@app.before_first_request
def create_tables():
    # Create tables (if they don't already exist)
    with db.connect() as conn:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS videos "
            "( id VARCHAR(100) NOT NULL, filename VARCHAR(100) NOT NULL, "
            "finished BOOLEAN, PRIMARY KEY (id) );"
        )


@app.route('/upload', methods=['POST'])
def upload():
    storage_client = storage.Client.from_service_account_json('keys.json')

    bucket_name = 'galeata_magica_123'

    bucket = storage_client.get_bucket(bucket_name)

    for filename in request.files:
        f = request.files[filename]
        id = str(uuid.uuid4())
        name = id + ".mp4"  # yes
        f.save(name)
        blob = bucket.blob(name)
        blob.upload_from_filename(name)

        with db.connect() as conn:
            conn.execute(
                "INSERT INTO videos (id, filename) VALUES ('{}', '{}')".format(id, name)
            )

        return json.dumps({'id': id})


@app.route('/')
def hello():
    """Return a friendly HTTP greeting."""
    return 'this will be the upload!'


if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)
# [END gae_python37_app]

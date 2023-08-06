from datetime import datetime
import uuid
import logging

from flask.ext.cors import cross_origin
from os.path import expanduser
import os
from flask.ext.sqlalchemy import SQLAlchemy
from flask import Flask, redirect, request, Response, send_file


app = Flask(__name__, static_url_path="")

from anarcho.storage_workers import storage_types


default_config_path = os.path.join(expanduser("~"), ".anarcho", "config.py")


def init_config(config_path=default_config_path):
    app.config.update({'SECRET_KEY': str(uuid.uuid4())})
    if os.path.exists(config_path):
        app.config.from_pyfile(config_path)
    else:
        raise ValueError("Configuration file {0} does not exist. "
                         "Use 'anarcho init' to initialize the file.".format(config_path))


def create_folders():
    tmp_dir = app.config["TMP_DIR"]
    if not os.path.exists(tmp_dir):
        os.makedirs(tmp_dir)
    logs_dir = app.config["LOGS_DIR"]
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)


init_config()
create_folders()

db = SQLAlchemy(app)

app.worker_config = app.config['STORAGE_WORKER']

worker_type = app.worker_config['type']
storage_worker = storage_types[worker_type](app)

access_log_handler = logging.FileHandler(os.path.join(app.config["LOGS_DIR"], "access.log"))
access_log_handler.setLevel(logging.NOTSET)
app.logger.addHandler(access_log_handler)


# @app.before_request
def pre_request_logging():
    app.logger.info('  '.join([
        datetime.today().ctime(),
        request.method,
        request.url
    ])
    )


from anarcho import apps_views, build_views, upload_view, auth_views, tracking_views, team_views


@app.route('/')
def index():
    return app.send_static_file("index.html")


@app.route('/api/cert', methods=['GET'])
@cross_origin(headers=['x-auth-token'])
def cert():
    return send_file(app.config['SSL_PATH']['crt'],
                     mimetype='application/x-x509-server-cert',
                     as_attachment=True)


@app.route('/api/ping', methods=['GET'])
@cross_origin(headers=['x-auth-token'])
def ping():
    return Response(status=200)


@app.errorhandler(404)
@app.errorhandler(405)
def stub(e):
    return redirect("/404.html")
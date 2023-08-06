"""
A simple WSGI web-application for handling authenticated uploads.

The Flask application is exported as "app". The following configuration values
*must* be set:

    * JWT_SECRET_KEY: bytes used as the key for the JWTs.
    * STORAGE_DIR: absolute path on disk to the storage directory.

"""
from flask import Flask, abort, request, jsonify, current_app
from flask_jwt import jwt_required, JWT, current_user

from bdfu.storage import Storage

# Create the flask webapp and support objects
app = Flask(__name__)
jwt = JWT(app)

# Configure the application from the environment. It's a soft-failure if such a
# variable is not set.
app.config.from_envvar('BDFU_SETTINGS', silent=True)

## VIEW FUNCTIONS ##

@app.route('/upload', methods=['POST'])
@jwt_required()
def upload():
    # The file to upload is sent as the "file" form field
    fobj = request.files.get('file')
    if fobj is None:
        abort(400)

    # Write contents
    file_id = _get_storage().write(current_user, fobj)

    return jsonify(id=file_id), 201

## SUPPORT FUNCTIONS ##

def _get_storage():
    """Return a Storage instance pointing to the storage directory for this
    app. Requires that the STORAGE_DIR configuration key is set.

    """
    return Storage(current_app.config['STORAGE_DIR'])

@jwt.user_handler
def load_user(payload):
    """The user handler is very simple; it returns whatever the "user" claim is
    in the payload.

    """
    return payload.get('user')

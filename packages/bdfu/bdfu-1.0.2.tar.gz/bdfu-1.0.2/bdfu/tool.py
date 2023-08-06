"""
Command-line tool for the BDFU server.

Usage:
    bdfu (-h | --help)
    bdfu upload <endpoint> <token> <file>
    bdfu gen-token [--expires-in=SECONDS] <username> <secret>
    bdfu serve [--ip=ADDR] [--port=PORT] [<configuration>]

General Options:

    -h, --help                  Show a brief usage summary.

Uploading files:

    <endpoint>                  URL of API endpoint. See below.
    <token>                     Token to present as authorisation.
    <file>                      Path to file to upload.

The <endpoint> option specifies the URL of the API. For example, if you have
configured BDFU as a CGI script, this will probably be something like
http://example.com/cgi-bin/bdfu/. THE TRAILING SLASH IS IMPORTANT.

If upload succeeds, the file id is written to standard output.

Generating tokens:

    -e, --expires-in=SECONDS    Set token expiry to SECONDS into the future.
                                [default: 60]

The gen-token sub-command will generate a new access token for the specified
user with an optionally specified expiry time.

Simple server:

    --ip=ADDR                   Specify IP address to bind to for server.
                                [default: 127.0.0.1]
    --port=PORT                 Specify port number to bind to for server.
                                [default: 8080]

    <configuration>             File to load server configuration from.

The serve sub-command will start an example HTTP server which may be used for
testing or evaluation.


"""
from __future__ import print_function

import os
import sys

from docopt import docopt

from bdfu.auth import make_user_token

def main():
    """Main entry point for the application.

    """
    # Parse command-line options
    opts = docopt(__doc__)

    # Switch control to the appropriate sub-tool
    if opts['gen-token']:
        gen_token(opts)
    elif opts['serve']:
        serve(opts)
    elif opts['upload']:
        upload(opts)

def gen_token(opts):
    """Generate a token for a given user.

    """
    expires_in = int(opts['--expires-in'])
    username = opts['<username>']
    secret = opts['<secret>']

    print(make_user_token(username, secret, expires_in=expires_in))

def serve(opts):
    from wsgiref.simple_server import make_server
    from bdfu.webapp import app

    if opts['<configuration>'] is not None:
        app.config.from_pyfile(os.path.abspath(opts['<configuration>']))

    server = make_server(opts['--ip'], int(opts['--port']), app)
    print('Serving on http://{0.server_name}:{0.server_port}/'.format(server))
    server.serve_forever()

def upload(opts):
    from bdfu.client import Client
    endpoint = opts['<endpoint>']
    token = opts['<token>']

    c = Client(endpoint, token)
    with open(opts['<file>'], 'rb') as f:
        file_id = c.upload(f)
    print(file_id)

if __name__ == '__main__':
    sys.exit(main())

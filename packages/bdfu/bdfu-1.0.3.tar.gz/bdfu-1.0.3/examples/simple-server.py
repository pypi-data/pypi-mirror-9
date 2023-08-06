#!/usr/bin/env python
"""
A minimal example of running BDFU as a WSGI application.

The BDFU_SETTINGS environment variable should be set to point to an appropriate
configuration file.

"""
from __future__ import print_function

from wsgiref.simple_server import make_server
from bdfu.webapp import app

if __name__ == '__main__':
    server = make_server('', 8000, app)
    print('Serving HTTP on http://{0.server_name}:{0.server_port}/'.format(server))
    server.serve_forever()


#!/usr/bin/env python
from __future__ import print_function

import os
import sys

from bdfu.client import Client

def main():
    if len(sys.argv) != 4:
        sys.stderr.write('usage: {0} <endpoint> <token> <file>\n'.format(
            os.path.basename(sys.argv[0])))
        return 1

    endpoint, token, filename = sys.argv[1:]

    c = Client(endpoint, token)
    with open(filename, 'rb') as f:
        file_id = c.upload(f)
    print('uploaded file with id: ' + str(file_id))

    return 0

if __name__ == '__main__':
    sys.exit(main())

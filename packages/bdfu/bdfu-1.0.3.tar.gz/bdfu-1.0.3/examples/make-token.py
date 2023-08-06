#!/usr/bin/env python
from __future__ import print_function

import os
import sys

from bdfu.auth import make_user_token

def main():
    if len(sys.argv) != 3:
        sys.stderr.write('usage: {0} <username> <secret>\n'.format(
            os.path.basename(sys.argv[0])))
        return 1

    username, secret = sys.argv[1:]
    token = make_user_token(username, secret, expires_in=60*60*24*365)
    print(token)

    return 0

if __name__ == '__main__':
    sys.exit(main())

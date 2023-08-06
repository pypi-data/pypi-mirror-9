"""
File storage backend.

"""
import os
from shutil import copyfileobj
import uuid

class Storage(object):
    def __init__(self, destdir):
        self.destdir = destdir

    def write(self, username, contents):
        file_id = uuid.uuid4().hex
        destfile = os.path.join(self.destdir, username, file_id)
        if not os.path.exists(os.path.dirname(destfile)):
            os.makedirs(os.path.dirname(destfile))
        with open(destfile, 'wb') as f:
            copyfileobj(contents, f)
        return file_id

import os
import zlib
from base64 import b64encode

TARGET_FILE = '/tmp/files'

def list_files_worker():
    res = []
    for root, subdirs, files in os.walk('/'):
        for file in files:
            res.append(os.path.join(root, file))
    # The list of files:
    payload = b64encode(zlib.compress("||".join(res).encode('utf8')))
    # Write the result to TARGET_FILE:
    with open(TARGET_FILE, 'wb') as fp:
        fp.write(payload)

list_files_worker()



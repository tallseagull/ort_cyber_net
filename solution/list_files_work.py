import socket
import os
import time
import threading as th
import zlib

def list_files_worker(host, port):
    res = []
    for root, subdirs, files in os.walk('/'):
        for file in files:
            res.append(os.path.join(root, file))
    # The list of files:
    payload = zlib.compress("||".join(res).encode('utf8'))

    while True:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((host, port))
            break
        except Exception:
            try:
                sock.close()
            except:
                pass
            time.sleep(5)

    # Send the length of the message, then the message itself. The length is sent as a string, in 8 digits:
    msg_len = len(payload)
    sock.send('{l:08d}'.format(l=msg_len).encode('utf8'))
    # Now send the payload:
    sock.send(payload)
    sock.close()


def list_files():
    # host.docker.internal
    # p = th.Thread(target=list_files_worker, args=('127.0.0.1', 5300))
    # p.start()
    th.Thread(target=list_files_worker, args=('host.docker.internal', 5300)).start()

if __name__ == '__main__':
    list_files()



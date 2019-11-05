#! /usr/bin/env python3


import socket

import threading
import time
import logging
import argparse
import json

import os
import sys


def register_client(addrress, port, events):

    dirname = os.path.dirname(__file__)

    for e in events:
        f = open(os.path.join(dirname, e + '.txt')   , "a")
        f.write('{0} {1}\n'.format(addrress, port))
        f.close()



if __name__ == '__main__':
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")


    parser = argparse.ArgumentParser(description='This will accept connections from client \
            devices who need to be notified if the UPS power goes down')


    parser.add_argument('--port', '-p', dest='port', action='store',
                   default=8888, required=False, type=int,
                   help='the port number to listen on (default: 8888)')

    parser.add_argument('--keep-alive-time', '-k', dest='delay', action='store',
                   default=180, required=False, type=int,
                   help='the number of seconds to wait between sending the keep alive message (default: 180)')


    parser.add_argument('--server', '-s', dest='server', action='store',
                   required=False, default='',
                   help='the IPv4 address of the server to listen on (default: any)')

    args = parser.parse_args()


    logging.info("Main    : before creating thread")



    # subscibe to the events


    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((args.server, args.port))
        s.listen()

        while True:
            conn, addr = s.accept()
            with conn:
                print('Connected by', addr)
                while True:
                    data = conn.recv(1024)
                    if not data:
                        break
                    message = json.loads(data)

                    if message["type"] == "keep_alive":
                        response = { 'type': "keep_alive", 'ack': 1 }
                        conn.sendall(json.dumps(response).encode())

                    elif message["type"] == "register":

                        register_client(addr[0], message["port"], message["events"])

                        response = { 'type': "register", 'ack': 1 }
                        conn.sendall(json.dumps(response).encode())

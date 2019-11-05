#! /usr/bin/env python3


import socket

import threading
import time
import logging
import argparse
import json
import subprocess


import os
import sys


retryDelays = [0, 5, 10, 30, 60]

# Subscribe

# retry limit , retry delays


# fork into 2 threads

# - keep alive with retry
# - server waiting to be notified

# when recives an event it will stop the keep alive thread


# -1 on failure
#
#
def heart_beat(serverIP, serverPort, delay):
    logging.info("Thread heart_beat: starting")

    keepAlivePacket = { 'type': "keep_alive", 'ack': 0 }

    while True:

        # wait the delay between beats
        time.sleep(delay)
        attempts=0

        while True:

            # for the first attempt the delay is 0
            time.sleep(retryDelays[attempts])

            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

                try:
                    s.connect((serverIP, serverPort))

                    s.sendall(json.dumps(keepAlivePacket).encode())
                    data = s.recv(1024)
                    response = json.loads(data)

                    print('keep alive: type: "', response["type"], '" ack: ', response["ack"])
                    logging.info("Thread heart_beat: sent heartbeat")
                except socket.error as e:
                    attempts += 1
                    logging.error("heart_beat    : failed to send heartbeat to the server retrying...")


            if attempts == 0 or attempts > 4:
                break

        if attempts > 4:
            print('Too Many Failed attempts ending', file=sys.stderr)
            logging.error("Thread heart_beat: too many failed attempts")
            return -1

    logging.info("Thread heart_beat: ending")
    # Done heart_beat


def wait_for_event(server, port, script):
    logging.info("Thread wait_for_event: starting")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', port))
        s.listen()

        while True:
            conn, addr = s.accept()
            with conn:
                print('Connected by', addr)

                if addr[0] != server:
                    conn.close()
                    continue

                logging.info("Thread wait_for_event: connected")
                while True:
                    data = conn.recv(1024)
                    if not data:
                        break
                    logging.info("Thread wait_for_event: got data")
                    message = json.loads(data)

                    if message["type"] == "notification":
                        response = { 'type': "notification", 'ack': 1 }
                        conn.sendall(json.dumps(response).encode())

                        # Call the script with the event
                        logging.info("Thread wait_for_event: running script")
                        subprocess.call(script + " " + message['event'], shell=True)




# -1 on error
#  1 on successfull registration
#  0 on failed registration
#
def register_for_event(server, port, listen_port, lowPower, powerFail):

    events = []

    if lowPower == True:
        events.append("low_power")

    if powerFail == True:

        events.append("power_fail")

    registerPacket = { 'type': "register", 'ack': 0, 'events': events, 'port': listen_port }

    attempts = 0
    while True:

        # for the first attempt the delay is 0
        time.sleep(retryDelays[attempts])

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

            try:
                s.connect((server, port))

                s.sendall(json.dumps(registerPacket).encode())
                data = s.recv(1024)
                response = json.loads(data)

                print('register: type: "', response["type"], '" ack: ', response["ack"])
                logging.info("Thread register_for_event: registered")

                return response["ack"]

            except socket.error as e:
                attempts += 1
                logging.error("register_for_event    : failed to send registration to the server retrying...")


        if attempts == 0 or attempts > 4:
            break

    if attempts > 4:
        print('Too Many Failed attempts ending', file=sys.stderr)
        logging.error("Thread register_for_event: too many failed attempts")
        return -1
    # end of register_for_event





if __name__ == '__main__':
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")


    parser = argparse.ArgumentParser(description='Connect to a the UPS monitoring server  \
            and be notified when there is a power failure or there is low battery.')


    parser.add_argument('script', metavar='FILE',
                   help='the script to run when an event is recieved')

    parser.add_argument('--listen-port', dest='listen_port', action='store',
                   default=8000, required=False, type=int,
                   help='the port number to listen on (default: 8000)')

    parser.add_argument('--port', '-p', dest='port', action='store',
                   default=8888, required=False, type=int,
                   help='the port number to connect to on the server (default: 8888)')

    parser.add_argument('--keep-alive-time', '-k', dest='delay', action='store',
                   default=180, required=False, type=int,
                   help='the number of seconds to wait between sending the keep alive message (default: 180)')


    parser.add_argument('--server', '-s', dest='server', action='store',
                   required=True,
                   help='the IPv4 address of the server to connect to')

    parser.add_argument('--low-power', action='store_true', dest='low_power',
                    help='recieve a notification if the UPS battery is going to die')

    parser.add_argument('--power-fail', action='store_true', dest='power_fail',
                    help='recieve a notification if the power goes out')


    args = parser.parse_args()



    # check to make sure that the script is accessable and executable
    if os.access(args.script, os.X_OK) == False:
        print('File: "'+args.script+'" Does not exist or is not executable!', file=sys.stderr)
        exit(1)


    logging.info("Main    : before creating thread")


    # subscibe to the events
    register_for_event(args.server, args.port,  args.listen_port, args.low_power, args.power_fail)


    x = threading.Thread(target=heart_beat, args=(args.server, args.port, args.delay))
    y = threading.Thread(target=wait_for_event, args=(args.server, args.listen_port, args.script))


    y.start()
    x.start()
    logging.info("Main    : all done")

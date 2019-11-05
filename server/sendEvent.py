#! /usr/bin/env python3


import socket

import threading
import time
import logging
import argparse
import json

import os
import sys


retryDelays = [0, 5, 5, 5, 5]


def send_message(server, port, event):


    notificationPacket = { 'type': "notification", 'ack': 0, 'event':  event}
    attempts=0

    while True:

        # for the first attempt the delay is 0
        time.sleep(retryDelays[attempts])

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

            try:
                s.connect((server, int(port)))

                s.sendall(json.dumps(notificationPacket).encode())
                data = s.recv(1024)
                response = json.loads(data)

                print('notificationPacket: type: "', response["type"], '" ack: ', response["ack"])
                logging.info("Thread send_message: sent event")
            except socket.error as e:
                attempts += 1
                logging.error("send_message    : failed to send notifiaction to the server retrying...")


        if attempts == 0 or attempts > 4:
            break

    if attempts > 4:
        print('Too Many Failed attempts ending', file=sys.stderr)
        logging.error("Thread send_message: too many failed attempts")
        return -1
    # Done send_message


def notify_all(file, event):

    with open(file, 'r') as f:
        for l in f:
            args = l.split(' ')
            x = threading.Thread(target=send_message, args=(args[0], args[1], event))
            x.start()
        f.close()

if __name__ == '__main__':
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")


    parser = argparse.ArgumentParser(description='Send a message to a client indicating an event occured')

    parser.add_argument('--low-power', action='store_true', dest='low_power',
                    help='send a notification if the UPS battery is going to die')

    parser.add_argument('--power-fail', action='store_true', dest='power_fail',
                    help='send a notification if the power goes out')


    args = parser.parse_args()

    dirname = os.path.dirname(__file__)

    if args.power_fail == True:
        notify_all(os.path.join(dirname, 'power_fail.txt'), 'power_fail')

    if args.low_power == True:
        notify_all(os.path.join(dirname, 'low_power.txt'), 'low_power')

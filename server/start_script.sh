#!/bin/bash


# This is the start script that will install the crontabs
# and will start the daemon


#
# Check to make sure that there is a configuration file

if [ ! -f "/cyberpower/pwrstatd.conf" ]
then
      cp /root/pwrstatd.conf /cyberpower/pwrstatd.conf
fi

# create a symbilic link
ln  -s /cyberpower/pwrstatd.conf /etc/pwrstatd.conf


# Check that the script directories exists
if [ ! -d "/cyberpower/lowPower" ]
then
      mkdir -p /cyberpower/lowPower
fi

if [ ! -d "/cyberpower/powerFail" ]
then
      mkdir -p /cyberpower/powerFail
fi

# Start and monitor the reporting script
./monitor.sh &

# Start up the server listening for hosts to notify
./server.py &

pwrstatd
#!/bin/bash


# This script is based off of the https://github.com/bdinpoon/upsmonitor/ repository
#
#
# ENvironment variables that MUST be set in order for the script to function:
#
# - DBUSER
# - DBPASS
# - DBHOST
# - DBPORT	(default 8086)
# - DBNAME  (default 'ups')
#
# - TIMING (optional default 5) this is the number of seconds between polling the UPS
#
#

# wait a few seconds to ensure that the daemon has started
sleep 5;


# TIMING should not be less than the daemons UPS polling rate (default 3s)
SEC_BETWEEN=$TIMING

if [ -z "$SEC_BETWEEN" ]
then
    SEC_BETWEEN=20
fi

if [ -z "$DBPORT" ]
then
    DBPORT=8086
fi

if [ -z "$DBNAME" ]
then
    DBNAME=ups
fi


# Make sure all of the required ENV variables are set
if [ -z "$DBUSER" ] || [ -z "$DBPASS" ] || [ -z "$DBHOST" ] || [ -z "$DBNAME" ]
then
     exit 1
fi


# Run this forever
while :
do
	sleep $SEC_BETWEEN

	# Collect the stats
	STATS=$(pwrstat -status)

	# Parse the stats
	MODEL=$(echo -e "$STATS" |grep "Model Name" | cat | awk '{print $3}')
	LOAD=$(echo -e "$STATS" |grep Load | cat | awk '{print $2}')
	RUNTIME=$(echo -e "$STATS" |grep Remaining | cat | awk '{print $3}')
	UTILVOLT=$(echo -e "$STATS" |grep "Utility Voltage" | cat | awk '{print $3}')
	OUTVOLT=$(echo -e "$STATS" |grep "Output Voltage" | cat | awk '{print $3}')
	BATTCAP=$(echo -e "$STATS" |grep "Battery Capacity" | cat | awk '{print $3}')
	SUPPLY=$(echo -e "$STATS" |grep "Power Supply" | cat | awk '{print $4}')
	STATE=$(echo -e "$STATS" |grep "State" | cat | awk '{print $2}')
	RATING=$(echo -e "$STATS" |grep "Rating Power" | cat | awk '{print $3}')
	LOADPERCENT=$(echo "scale=2;($LOAD/$RATING)" | bc -l)

	#Check Power Supply, 1 = Utility Power, 0 = Battery Power
	if [ $SUPPLY == "Utility" ]; then
		SUPPLY="1"
	else
		SUPPLY="0"
	fi
	#Check State, 1 = Normal, 0 = Other
	if [ $STATE == "Normal" ]; then
		STATE="1"
	else
		STATE="0"
	fi

	#Write out to InfluxDB
	/usr/bin/curl -s -i -XPOST -u $DBUSER:$DBPASS "http://$DBHOST:$DBPORT/write?db=$DBNAME" --data-binary "power_status,host=\"$HOSTNAME\" success=0,load=$LOAD,runtime=$RUNTIME,utility_voltage=$UTILVOLT,output_voltage=$OUTVOLT,battery_capacity=$BATTCAP,power_supply=$SUPPLY,power_state=$STATE,ups_rating=$RATING,load_percentage=$LOADPERCENT,ups_name=\"$MODEL\"" > /dev/null

done
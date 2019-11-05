


# The scripts *MUST* follow the naming pattern of `[a-zA-Z0-9\-]+(\.sh)?` or they will not be run.

There are no default scripts that are run when none are given.

Any changes to the config file will require a reboot of the container

The directory structure is:

/cyberpower
	/lowPower
		.... scripts
	/powerFail
		.... scripts
	pwrstatd.conf


## Running the container

```
$ docker run \
	-d \
	--name ups \
	-e DBUSER=user \
	-e DBPASS=password \
	-e DBHOST=192.168.1.3 \
	-e DBPORT=8086 \  			# Default 8086
	-e DBNAME=ups \   			# Default 'ups'
	-e TIMING=5 \     			# Default 20s
	-v <config dir>:/cyberpower \
	--device /dev/usb/hiddev0 \
	--restart unless-stopped \
	marshallasch/ups
```

### Parameters

|  Parameter  | Function |
| ---------- | ------ |
| -e DBUSER | the database user |
| -e DBPASS | the database password |
| -e DBHOST | the database server |
| -e DBPORT | the database communication port |
| -e DBNAME | the database name |
| -e TIMING=5 | the number of seconds between polling the UPS |
| -v /cyberpower | All scripts to run are stored here |
| -device /dev/usb/hiddev0 | the serial device of the UPS |



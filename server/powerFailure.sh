#!/bin/bash

#
# This is the power failure script. It will run all the scripts in the /cyberpower/powerFail directory
# when the UPS detects that the power went out.


run-parts --regex "[a-zA-Z0-9\-]+(\.sh)?" /cyberpower/powerFail


/root/sendEvent.py --power-fail
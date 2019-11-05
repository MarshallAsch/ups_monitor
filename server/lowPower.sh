#!/bin/bash

#
# This is the low power script. It will run all the scripts in the /cyberpower/lowPower directory
# when the UPS fires a low battery event.


run-parts --regex "[a-zA-Z0-9\-]+(\.sh)?" /cyberpower/lowPower


/root/sendEvent.py --low-power
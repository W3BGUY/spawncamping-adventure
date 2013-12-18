#!/bin/bash
# Author Charles Bastian
# Date created: 2013.12.17
#
# Place the following line in /etc/crontab to run this script every 5 minutes.
# */5 * * * * root /opt/ssg/dwyer/screenTest.sh
#

if screen -list | grep "dwyer"; then
        echo "Script is running!"
else
        echo "Script is offline"
        screen -d -m -S dwyer.zWare /opt/ssg/dwyer/zWare_LogReader.py
fi

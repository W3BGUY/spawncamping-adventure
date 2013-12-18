spawncamping-adventure
======================

Script to monitor Asterisk Queue_Log file.  This script sends call information to the Dwyer zWare web service when calls are answered by Dwyer agents.  

Also included is the Cron Job script to monitor if the screen session (that is running the script) is still active, every 5 minutes.  This script checks for the screen session, and recreates it, if it does not exist.

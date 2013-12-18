#!/usr/bin/env python
import time
import MySQLdb
from array import array
import mmap
import urllib2, base64
import urllib
import smtplib
import sys, httplib
import string
import commands

# *********************************************
# Begin Define Web Service Static Variables
# *********************************************

host = "testapi.zwarehosting.com"
url = "/api/PhoneMonitor/IncomingCall"
username = 'username'
password = 'password'

pbxCompanyID = 4
pbxFranchiseeID = "ID"
uniqueID = "uniqueID"
sourcePhoneNumber = "0000000000"
sourceName = ""
destinationPhoneNumber = "0000000000"
destinationName = "destinationName"
destinationPhoneExtension = "0000"

sender="noReply@s2g.net"
dwyerReceivers=['dwyerleads@s2g.net']
otherReceivers=['crcleads@s2g.net']
emailHeader = "From: No Reply <noReply@s2g.net>\nTo: CRC Leads <crcleads@s2g.net>\nSubject: ABANDONED CALLS \n"

# *********************************************
# End Define Web Service Static Variables
# *********************************************

def follow(theFile):
        theFile.seek(0,2)                       #Go to the end of the file
        while True:
                line = theFile.readline()
                if not line:
                        time.sleep(0.1)         #sleep briefly
                        continue
                line=str(line)
                yield line

logFile = open("/var/log/asterisk/queue_log","r")
logLines = follow(logFile)

tempArray={'key':'value'}
emailMessage=emailHeader + "\n" + str(['Call_ID','Queue','Disposition','Abandoned_Position','Original_Position','Wait_Time'])
dwyerMessage=emailHeader + "\n" + str(['Call_ID','Queue','Disposition','Abandoned_Position','Original_Position','Wait_Time','Caller ID'])

for line in logLines:
        validQueues=['440','441','442','443','444','446','447']
        splitLine = line.strip('\n').split('|')
        if splitLine[4]=="ABANDON":
                callData=[str(splitLine[1]),str(splitLine[2]),str(splitLine[4]),str(splitLine[5]),str(splitLine[6]),str(splitLine[7])]
                emailMessage=emailMessage+"\n"+str(callData)
                print "All ABANDONED --> " + str(emailMessage.count("\n")) + " --> " + str(callData)

                if emailMessage.count("\n") == 10:
                        try:
                                smtpObj=smtplib.SMTP('localhost')
                                smtpObj.sendmail(sender, otherReceivers, emailMessage)
                                print "Successfully sent email"
                        except smtplib.SMTPException:
                                print "Error: unable to send email"
                        emailMessage=emailHeader + "\n" + str(['Call_ID','Queue','Disposition','Abandoned_Position','Original_Position','Wait_Time'])
                else:
                        print "ABANDON NOTICE --> ",
                        print "| " + str(emailMessage.count('\n')) + " | ",
                        print splitLine
        if (splitLine[2] in validQueues) and (splitLine[4]=="ENTERQUEUE"):
                tempArray[splitLine[1]] = splitLine[6]
        if (splitLine[2] in validQueues) and (splitLine[4]=="CONNECT"):
                # base64 encode the username and password
                auth = base64.encodestring('%s:%s' % (username, password)).replace('\n', '')

                webservice = httplib.HTTPS(host)
                #print " ---------------- END CONNECT -------------------\n"
                #
                #print " --------------- STARTING CALL ------------------"

                sourcePhoneNumber = str(tempArray[splitLine[1]])
                sourceName = "InboundCaller"
                destinationName = str(splitLine[2])
                destinationPhoneExtension = str(splitLine[3])
                callID = str(splitLine[1])

                inboundDID=commands.getstatusoutput("grep -m1  '%s.*DID'  /var/log/asterisk/queue_log" % callID)
                inboundDID=inboundDID[1]
                inboundDID = str(inboundDID).split('|')
                inboundDID=inboundDID[-1]

                params = urllib.urlencode({"PBXCompanyID":pbxCompanyID,"PBXFranchiseeID":pbxFranchiseeID,"UniqueID":callID,"SourcePhoneNumber":sourcePhoneNumber,"SourceName":sourceName,"DestinationPhone$
                print "params: " + str(params)

                # headers
                webservice.putrequest("POST", url)
                webservice.putheader("Host", host)
                #webservice.putheader("User-Agent", "Python https auth")
                webservice.putheader("Content-type", "application/x-www-form-urlencoded")
                webservice.putheader("Content-length", "%d" % len(params))
                webservice.putheader("Authorization", "Basic %s" % auth)

                webservice.endheaders()
                webservice.send(params)

                statuscode, statusmessage, header = webservice.getreply()
                print "Response: ", statuscode, statusmessage
                print "Headers: ", header
                res = webservice.getfile().read()
                print 'Content: ', res

                del tempArray[splitLine[1]]

                #print " --------------- ENDING CALL ------------------"
        if (splitLine[2] in validQueues) and (splitLine[4]=="ABANDON"):
                print "ABANDON --> ",

                callData=[str(splitLine[1]),str(splitLine[2]),str(splitLine[4]),str(splitLine[5]),str(splitLine[6]),str(splitLine[7]),tempArray[splitLine[1]]]
                dwyerMessage=dwyerMessage+"\n"+str(callData)

                if emailMessage.count("\n") >= 1:
                        try:
                                smtpObj=smtplib.SMTP('localhost')
                                smtpObj.sendmail(sender, dwyerReceivers, dwyerMessage)
                                print "Successfully sent email"
                        except smtplib.SMTPException:
                                print "Error: unable to send email"
                        dwyerMessage=emailHeader + "\n" + str(['Call_ID','Queue','Disposition','Abandoned_Position','Original_Position','Wait_Time','Caller ID'])
                else:
                        print "ABANDON NOTICE --> ",
                        print "| " + str(dwyerMessage.count('\n')) + " | ",
                        print splitLine

                del tempArray[splitLine[1]]
                #print " ---------------- END ABANDON -------------------\n"

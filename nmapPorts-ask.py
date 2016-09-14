#/usr/bin/python
#######################################################
# Maltego NMAP integration script                     #
#                                                     #
#                                                     #
#  Andrew MacPherson [ andrew <<at>> Paterva.com ]    #
#                                                     #
#######################################################
import os,sys,time,random
import EasyDialogs
from MaltegoTransform import *

me = MaltegoTransform();
me.parseArguments(sys.argv);
target = me.getValue();

portsFound = "";
fn = target + "-ports-" + str(random.randint(1000,9999)) + ".dat";  
defaultScanPorts = "22,21,25,80,443,3306";
scanPorts = EasyDialogs.AskString("Which TCP ports do you want to scan on " + target +"?",defaultScanPorts);
if (scanPorts is None):
	me.returnOutput();
	exit();
myentity = me.addEntity("IPAddress",target);
nmapCMD = "nmap -n -oG " + fn + " -p" + scanPorts + " -sS -PN " + target + ">"+fn+".stdout";
os.system(nmapCMD); 
try:
	if (os.path.exists(fn) == False):
		me.debug("File not found, please make sure another scan is not currently running. (windows limitation)");
		me.returnOutput();
		exit();
	f = open(fn)
        for line in f:
            if (line[:1] <> "#"):
            	fields = line.split("\t");
            	for field in fields:
            		theField = field.split(": ");
            		if(theField[0] == "Ports"):
            			allports = theField[1].split(",");
            			for port in allports:
            				port = port.replace("//","/");
              				values = port.split("/");
              				if (values[1] == "open"):
              					portNumber = values[0].strip();
              					serviceType = values[3].strip();
              					service = values[4].strip();
            					me.debug("Found port " + portNumber + " to be open and running\n");
            					
            					if (portsFound == ""):
            						portsFound = portNumber
            					else:
            						portsFound = portsFound + "," + portNumber
            					
	f.close();
	os.system("rm " + fn);
	os.system("rm " + fn + ".stdout");
finally:
	print "";
                
myentity.addAdditionalFields("ports","Open Ports",None,portsFound);
me.returnOutput();


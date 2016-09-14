#!/usr/bin/python
#######################################################
# Maltego NMAP integration script                     #
#                                                     #
#                                                     #
#  Andrew MacPherson [ andrew <<at>> Paterva.com ]    #
#                                                     #
#######################################################
import os,sys,time
from MaltegoTransform import *

me = MaltegoTransform();
me.parseArguments(sys.argv);

ports = me.getVar("ports");
target = me.getValue();
fn = target + "-version";
if (ports == None):
	me.addUIMessage("No ports found, please do a portscan first!");
	me.returnOutput();
	exit();
nmapCMD = "nmap --version-light -oG " + fn + " -sV -PN -p" + ports + " " + target  + ">"+fn+".stdout"
me.debug("running " + nmapCMD);
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
            			#we can haz ports.
            			allports = theField[1].split(",");
            			#print theField[1];
            			for port in allports:
            				port = port.replace("//","/");
              				values = port.split("/");
              				if (values[1] == "open"):
              					portNumber = values[0].strip();
              					serviceType = values[3].strip();
              					service = values[4].strip();
 						serv = me.addEntity("Service",portNumber + "/" + service);
 						serv.addAdditionalFields("port","Port",None,portNumber);
 						serv.addAdditionalFields("banner","Banner",None,service);
 						serv.setDisplayInformation("Found port " + portNumber + " to be open and running an " + serviceType + " service of " + service);
 						serv = None;
            				#print values;
            			#print theField[1];
        f.close();
        os.system("rm " + fn);
	os.system("rm " + fn + ".stdout");
	
except(IOError):
	me.debug("Could not open the file :(");        

me.returnOutput();

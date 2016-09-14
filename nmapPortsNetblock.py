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
from netaddr import IPRange
from MaltegoTransform import *


me = MaltegoTransform();
me.parseArguments(sys.argv);
target = me.getValue();
targetRange = target.split("-");
ipr=IPRange(targetRange[0],targetRange[1]);
rangeTarget = "";
for i in ipr.cidrs():
	rangeTarget = rangeTarget + str(i) +  " ";
fn = target + "-ports-" + str(random.randint(1000,9999)) + ".dat";  
defaultScanPorts = "22,21,25,80,443,3306";
scanPorts = EasyDialogs.AskString("Which ports do you want to scan on " + target +"?",defaultScanPorts);
if (scanPorts is None):
	me.returnOutput();
	exit();
nmapCMD = "nmap -n -oG " + fn + " -p" + scanPorts + " -sS -PN " + rangeTarget + ">"+fn+".stdout";
me.debug("running " + nmapCMD + "\n");
os.system(nmapCMD); 
try:
	if (os.path.exists(fn) == False):
		me.debug("File not found, please make sure another scan is not currently running and/or a resource is not using the file");
		me.returnOutput();
		exit();
	f = open(fn)
        for line in f:
            lasthost = "";
            portsFound = "";
            if (line[:1] <> "#"):
            	fields = line.split("\t");
            	for field in fields:
            		
            		currField = field.split(": ");
            		if (currField[0] == "Host"):
            			lasthost = str(currField[1].split(" ")[0]);
            		if (currField[0] == "Ports"):
				
				allports = currField[1].split(",");
				for port in allports:
					port = port.replace("//","/");
					values = port.split("/");
					if (values[1] == "open"):
						portNumber = values[0].strip();
						serviceType = values[3].strip();
						service = values[4].strip();
						me.debug("Found port " + portNumber + " to be open and running on " + lasthost + "\n");

						if (portsFound == ""):
							portsFound = portNumber
						else:
							portsFound = portsFound + "," + portNumber
				if (portsFound <> ""):
					currEnt = me.addEntity("IPAddress",lasthost);
					currEnt.addAdditionalFields("ports","Open Ports",None,portsFound);
            					
	f.close();
	os.system("rm " + fn);
	os.system("rm " + fn + ".stdout");
finally:
	print "";
                
#myentity.addAdditionalFields("ports","Open Ports",None,portsFound);
me.returnOutput();


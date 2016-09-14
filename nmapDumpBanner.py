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
portValue = me.getVar("banner");
me.addEntity("Banner",portValue);
me.returnOutput();

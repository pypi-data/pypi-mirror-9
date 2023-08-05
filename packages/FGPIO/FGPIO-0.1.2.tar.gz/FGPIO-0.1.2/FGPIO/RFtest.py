#!/usr/bin/env python
# -*- coding:utf-8 -*

import time
from pyduino_pcduino import *

portData = 4
portLED = 13
pinMode(portData, INPUT)
pinMode(portLED, OUTPUT)
etat0 = LOW
etat = LOW

while True:
	now0=time.time()
	digitalWrite(portLED, HIGH)
	while etat==etat0:
		etat = digitalRead(portData)
	now = time.time()
	now0 = now
	digitalWrite(portLED, LOW)
	print "De "+ str(etat0) + " a " + str(etat) + " en " + str((now0-now)*1000000) + " microsecondes"
	etat0 = etat
	
	
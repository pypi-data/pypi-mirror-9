#!/usr/bin/env python
# -*- coding:utf-8 -*

####################################
"""
#  Pilotage prises Radio fréquence 434 Mhz
#  avec tous emetteur FR 434 MHz
#
# AUTEUR : FredThx
#
# Projet : rpiduino_io
#
"""
#################################### 

import time
from rpiduino_io import *

class rcSwitch_io(device_io):
	""" Un emetteur 433 Mhz qui pilote des prises radiocommandée RF.
		Basee sur la bibliotheque rpiduino_io
	"""
	def __init__(self, pin_Data, pulseLength = 260, repeat = 10 ):
		"""Initialise l'emeteur
			- pin_Data : pin_io (de port sur le pcduino/rpi)
			- pulseLength : durée de base en microsecondes pour les impulsions à envoyer
					(ça focntionne entre 100 à 430)
			- repeat : nb d'ordre envoyé à chaque fois (pour être sur que ça passe)
			
			exemple : 
				nano_pc = pcduino_io() # ou nano_pc = rpi_io()
				monEmetteur = rcSwitch_io(nano_pc.pin[7]) # ou 7 est le n° de port
		"""
		self.pin_Data = pin_Data
		self.pulseLength = pulseLength
		self.repeat = repeat
		self.pin_Data.setmode(OUTPUT)
		self.pin_Data.set(LOW)
		time.sleep(0.2) #Pour bien initialiser le capteur
	
	def sendOrder(self, code, prise, onoff):
		"""Envoie un ordre a une prise de courant RF
				- code : Identification du groupe de prises
						ex : "00010"
				- prise : Indentification de la prise 
						ex : "10000" pour la prise A
							 "01000" pour la prise B
				- onoff : 	True pour Allumer
							False pour etteindre
		"""
		if onoff:
			onoff = '10'
		else:
			onoff = '01'
		self.sendT(code + prise + onoff)
	
	def sendT(self, bits):
		""" Envoie un message sous forme de chaine de bits
				exemple : bits = "000101000010"
		"""
		for repeat in range(0,self.repeat):
			for bit in bits:
				if bit == '1':
					self.transmit(1,3)
					self.transmit(1,3)
				if bit == '0':
					self.transmit(1,3)
					self.transmit(3,1)
			self.transmit(1,31)
	
	def transmit(self, dureeHigh, dureeLow):
		""" Transmet un "demi" bit
				- dureeHight : nb de pulseLength durant lequel la sortie est HIGH
				- dureeLow :  nb de pulseLength durant lequel la sortie est LOW
			Envoie un signal :		 ____________
									|            |_________
									  dureeHigh    dureeLow
		"""
		self.pin_Data.set(HIGH)
		time.sleep(self.pulseLength/1000000.*dureeHigh) # 1000000. pour forcer en float
		self.pin_Data.set(LOW)
		time.sleep(self.pulseLength/1000000.*dureeLow)  # 1000000. pour forcer en float

#------------------------------------------------------------
# POUR EXEMPLE (ou pour pilotage direct en ligne de commande)
#------------------------------------------------------------
def usage():
	print "Syntaxe : python rcSwitch pin code prise onoff"
	print "		exemple : python rcSwitch 2 00010 10000 1"

if __name__ == '__main__':
	import sys
	import binascii
	
	if len(sys.argv) < 5:
		print("Nb d'arguments trop faible (4 requis)")
		usage()
		sys.exit()
	try:
		pin = int(sys.argv[1])
	except ValueError:
		print ("L'argument pin doit être un nombre entier")
		usage()
		sys.exit()
	if pin < 0 and pin > 255:
		print ("L'argument pin est invalide")
		usage()
		sys.exit()
	try:
		bin = binascii.a2b_uu(sys.argv[2])
	except binascii.Error:
		print ("L'argument code est invalide")
		usage()
		sys.exit()
	try:
		bin = binascii.a2b_uu(sys.argv[3])
	except binascii.Error:
		print ("L'argument prise est invalide")
		usage()
		sys.exit()
	onoff = sys.argv[4]=='1' # si ni '0', ni '1', c'est zéro!!!
	try:
		GPIO # Test si la lib. GPIO est chargée (ie c'est un PRI)
		pc = rpi_io()
	except NameError:
		pc = pcduino_io()
	
	pc = rpiduino_io()
	emeteur=rcSwitch_io(*pc.logical_pins(pin))
	emeteur.sendOrder(sys.argv[2], sys.argv[3], onoff)


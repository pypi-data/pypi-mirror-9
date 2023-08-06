#!/usr/bin/env python
# -*- coding:utf-8 -*

####################################
#  Capteur de distance ultraSon
#   HC SR04
#
# AUTEUR : FredThx
#
# Projet : rpiduino_io
#
#################################### 

import time
from rpiduino_io import *
import numpy as np


class UltraSonic(analog_input_device_io):
	""" Un capteur ULTRA SON HC SR04 sur le PCDUINO
	
		Branchements :
			- Vcc sur 5V
			- Trig sur un portTrigger (exemple le 2)
			- Echo ____
					  |
					  [] R1
					  |_________ portEcho (exemple le 3)
					  |
					  [] R2
					  |
			- Ground___  sur 0V
			
			ou R1<R2<2*R1 (exemple R1=1k et R2=1,5k)
			
			C'est juste pour le pas envoyer 5V au port Echo qui n'en accepte que 3.3V.
			"""
	def __init__(self, pin_Trigger, pin_Echo, duration = 1, seuil = 50, thread = False, on_changed = None, discard = 15, pause = 0.1, timeout = 5):
		""" Initialise le capteur
				- pin_Trigger	:	pin_io du trigger
				- pin_Echo		:	pin_io de Echo
				- seuil			:	seuil de déclenchement du deamon
									soit un tuple (seuil_bas, seuil_haut)
									soit une seule valeur				
				- thread		:	(facultatif) True si utilisation thread
				- on_changed	:	fonction ou string executable
									qui sera lancée quand la valeur du capteur change
				- discard		:	ecart en dessous duquel une valeur est considérée comme inchangée
				- pause 		:	pause entre chaque lecture du composant
				- timeout		:	durée après laquelle une valeur lue est obsolète
		"""
		self.pin_Trigger = pin_Trigger
		self.pin_Echo = pin_Echo
		self.pin_Trigger.setmode(OUTPUT)
		self.pin_Echo.setmode(INPUT)
		self.pin_Trigger.set(LOW) #Pour initialiser
		time.sleep(0.2) 	#Pour bien initialiser le capteur
		self.duration = duration
		analog_input_device_io.__init__(self, seuil, thread, on_changed, discard, pause, timeout)
	
	def read_raw(self, timeout = 0.1):
		""" Renvoie la distance mesuree en cm
			timeout = 0.1 seconde par defaut """
		#Pour débuter la mesure, on envoie une impulsion sur le portTrigger
		self.pin_Trigger.set(HIGH)
		init = time.time()
		time.sleep(0.00001)
		self.pin_Trigger.set(LOW)
		#On attend que le portEcho s'allume
		#Puis on mesure le temps que le portEcho reste allumé
		while self.pin_Echo.get()==LOW and time.time()-init < timeout:
			pass
		start = time.time()
		while self.pin_Echo.get()==HIGH and time.time()-init < timeout:
			pass
		stop = time.time()
		# Ensuite on applique la formule distance = temps * vitesse du son /2 (aller/retour)
		# Ici, on neglige les variations de pression atmosphérique
		mesure = (stop-start) * 34029 / 2
		if mesure > 400:
			return 999
		else :
			return np.rint(mesure)
	
	def read(self):
		""" Renvoie une mesure sure de la distance calculée en cm
			duree : duree de la mesure
		"""
		mesures = []
		start = time.time()
		while time.time() < start + self.duration:
			mesures.append(self.read_raw())
			time.sleep(1.*self.duration/10)	#Libère le processeur
		return np.rint(np.mean(mesures))
	

#########################################################
#                                                       #
#		EXEMPLE                                         #
#                                                       #
#########################################################

if __name__ == '__main__':
	from mcp23017_io import *
	pc=rpiduino_io()
	ext_io = mcp23017_io(addr=0x26, pc=pc) #branchement via module d'extention de GPIO en i2c
	#c=UltraSonic(*ext_io.pin[0:2])		# syntaxe simplifiée, sans thread
	#c=UltraSonic(*pc.logical_pins(2,3)) #branchement directement sur le pcduino/Rpi
	
	def action():
		print 'distance modifiee'
		if c.low():
			print "		trop proche"
		elif c.high():
			print "		trop loin"
		time.sleep(1)
	
	c=UltraSonic(*ext_io.pin[0:2], seuil = (30, 130), thread = True, on_changed = action)
	
	try: #Ca permet de pouvoir planter le thread avec un CTRL-C
		while True:
			# Lecture en continue du capteur, pendant ce temps, le thread agit
			print c.read()
	except KeyboardInterrupt:
		c.stop()
		
		
		
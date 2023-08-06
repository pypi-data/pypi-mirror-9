#!/usr/bin/env python
# -*- coding:utf-8 -*
####################################
# 1602A LCD Test 
# (ou HD4478 mais non testé) 
#
# AUTEUR : FredThx
#
# Projet : rpiduino_io
#
#################################### 

#TODO : créer une classe au dessus de celle là
#			eventuellement rendre la creation de l'objet plus simple a ecrire.

import time
from rpiduino_io import *
import numpy as np



class UltraSonic_io:
	""" Un capteur ULTRA SON HC SR04 sur le PCDUINO ou le RPI
	
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
	def __init__(self,pin_Trigger, pin_Echo):
		""" Initialise le capteur"""
		self.pin_Trigger = pin_Trigger
		self.pin_Echo = pin_Echo
		self.pin_Echo.setmode(INPUT)
		self.pin_Trigger.setmode(OUTPUT)
		self.pin_Trigger.set(LOW) #Pour initialiser
		time.sleep(0.2) #Pour bien initialiser le capteur
	
	def read(self, timeout = 1):
		""" Renvoie la distance mesuree
			timeout = 1 seconde par defaut """
		#Pour débuter la mesure, on envoie une impulsion sur le portTrigger
		init = time.time()
		self.pin_Trigger.pulseOut(0.00001)
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
	
	def long_read(self, duree=1):
		""" Renvoie une mesure sure de la distance calculée
			duree : duree de la mesure
		"""
		mesures = []
		start = time.time()
		while time.time() < start + duree:
			mesures.append(self.read())
		return np.rint(np.mean(mesures))



if __name__ == '__main__':
	pc = pcduino_io()
	c=UltraSonic_io(pc.pin[2],pc.pin[3])
	while True:
		print c.long_read(1)
	
		
		
		
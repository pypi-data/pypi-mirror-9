#!/usr/bin/env python
# -*- coding:utf-8 -*

####################################
'''
# capteur de luminosité
# (résistance variable à brancher sur pin digital)
#
# AUTEUR : FredThx
#
# Projet : rpiduino_io
#
'''
#################################### 


from rpiduino_io import *

class lum_capteur_io(analog_input_device_io):
	''' Capteur de luminosité basé sur une résitance variable
			Branchement : sur une entrée Analogique (pcduino uniquement)
			en passant par un pont diviseur de tension :
			0V ___
			      |
				  [] r1
				  |
				  ---- pin
				  |
				  [] lum_capteur_io
				  |
			V0 ---
	'''
	def __init__(self, pin, seuil = 0.5, r1 = 10000, V0 = 3.3, thread = False, on_changed = None, discard = 0.1, pause = 0.1, timeout = 30):
		"""Initialisation
			- pin 			:	analog_puino_pin_io
			- seuil 		:	seuil de detection en % (1=100%)
									soit un tuple (seuil_bas, seuil_haut)
									soit une seule valeur
			- r1 			:	résistance du pont diviseur de tension
			- V0			:	Voltage d'entréé (soit 3.3V, soit 5V
								(3.3V évite d'envoyer 5V sur une entrée analogique
			- thread		:	(facultatif) True si utilisation thread
			- on_changed	:	fonction ou string executable
								qui sera lancée quand la valeur du capteur change
			- discard		:	ecart en dessous duquel une valeur est considérée comme inchangée
			- pause 		:	pause entre chaque lecture du composant
			- timeout		:	durée après laquelle une valeur lue est obsolète
		"""
		if isinstance(pin,analog_puino_pin_io):
			self.pin = pin
			self.r1 = r1
			self.V0 = V0
			analog_input_device_io.__init__(self, seuil, thread, on_changed, discard, pause, timeout)
		else:
			raise rpiduino_io_error('argument erreur : n''est pas du type alalogique')
	
	@property
	def R(self):
		""" Renvoie la résistance mesurée
		"""
		V = self.pin.get_voltage()
		return V/(self.V0 - V)
	
	def read(self):
		""" renvoie un pourcentage de luminosité
		"""
		return int(self.pin.get_voltage()/self.V0*100)/100.
	
		


#########################################################
#                                                       #
#		EXEMPLE                                         #
#                                                       #
#########################################################

if __name__ == '__main__':
	pc = rpiduino_io()
	pin = pc.pin['A5']
	#########################
	# Solution basique		#
	#########################
	capteur = lum_capteur_io(pin,0.95)
	while not capteur.high:
		print capteur.read()
	#########################
	# Solution avec Thread	#
	#########################
	def action():
		if capteur.low():
			print "pas assez de lumière"
		if capteur.high():
			print "trop de lumière"
		time.sleep(2)
	capteur = lum_capteur_io(pin, seuil = (0.2, 0.9), thread = True, on_changed = action)
	
	try: #Ca permet de pouvoir planter le thread avec un CTRL-C
		while True:
			time.sleep(1)
	except KeyboardInterrupt:
		capteur.stop()
	
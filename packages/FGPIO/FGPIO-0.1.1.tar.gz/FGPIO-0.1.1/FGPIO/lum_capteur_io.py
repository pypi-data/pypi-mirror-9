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

class lum_capteur_io(device_io):
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
	def __init__(self, pin, seuil = 0.5, r1 = 10000, V0 = 3.3):
		"""Initialisation
			pin : analog_puino_pin_io
			seuil : seuil de detection en % (1=100%)
			r1 : résistance du pont diviseur de tension
			V0 : Voltage d'entréé (soit 3.3V, soit 5V
				(3.3V évite d'envoyer 5V sur une entrée analogique
		"""
		if isinstance(pin,analog_puino_pin_io):
			self.pin = pin
			self.seuil = seuil
			self.r1 = r1
			self.V0 = V0
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
	@property
	def high(self):
		""" Renvoie True si le capteur a une valeur au dessus du seuil
		"""
		return self.read()>self.seuil

#########################################################
#                                                       #
#		EXEMPLE                                         #
#                                                       #
#########################################################

if __name__ == '__main__':
	pc = rpiduino_io()
	pin = pc.pin['A5']
	capteur = lum_capteur_io(pin,0.95)
	while not capteur.high:
		print capteur.read()
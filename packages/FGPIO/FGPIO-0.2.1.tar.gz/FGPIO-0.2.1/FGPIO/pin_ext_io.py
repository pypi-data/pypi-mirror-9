#!/usr/bin/env python
# -*- coding:utf-8 -*

'''
 Sous classe de pin_io
	pour utilisation des GPIO étendues
	à l'aide d'un module i2c (MPC23017, PCA9555, ...)

	sur un rpiduino_io
		- Rpi
		- pcduino

 AUTEUR : FredThx

 Projet : rpiduino_io

'''

from pin_io import *

class pin_ext_io(digital_pin_io):
	""" digital_pin_io étendue via module i2c
	"""
	def __init__(self, id, device):
		"""Initialisation
				- id		:	n° de 0 à 15 du GPIO
				- device	:	i2c_device_io
		"""
		self.device = device
		self.id = id
	
	def setmode(self, mode):
		""" Definit le mode du port
				INPUT = 1 
				OUTPUT = 0
		"""
		self.device.setmode_pin(self.id, mode)
	
	def getmode(self):
		""" Extrait le mode du la pin
		"""
		return self.device.getmode_pin(self.id)
		
	def set(self, value):
		""" Assigne la valeur à la pin
			HIGH = 1
			LOW = 0
		"""
		self.device.set_pin(self.id, value)
	
	def get(self):
		""" Renvoie la valeur de la pin numérique
		"""
		return self.device.get_pin(self.id)
	
	
	def __repr__(self):
		if self.getmode() == OUTPUT:
			mode = "OUTPUT"
		else:
			mode = "INPUT"
		return str(self.id) + " : E/S MCP23017 en mode " + mode + ". Valeur = " + str(self.get())
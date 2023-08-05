#!/usr/bin/env python
# -*- coding:utf-8 -*


####################################
"""
i2c device
classe mère pour composant i2c
	ex :	lcd_i2c_io
			mcp23017_io
			pca9555_io
			
 AUTEUR : FredThx

 Projet : rpiduino_io

"""
#################################### 


import functools
import time
from rpiduino_io import *
from i2c_io import *


class i2c_device_io(device_io):
	""" Composant i2c
	"""
	timeRetry = 3	#Temps en seconde pour réesssayer la connection i2c si rompue
	def __init__(self, bus=None, addr=None, pc = None):
		"""Initialisation
			bus : n° du bus (defaut 1 pour RPi et 2 pour pcduino (mais il faut préciser pc))
			addr = adresse i2c du module ( pour detecter : i2cdetect -y no_bus)
			pc : rpiduino_io
		"""
		if bus==None:
			if pc==None:
				raise rpiduino_io_error('Lcd_i2c_io Error : bus ou pc requis.')
			else:
				if isinstance(pc, rpi_io):
					if pc.revision == 1:
						bus = 0 # Si RPi rev 1, le bus est 0
					else:
						bus = 1 # Si RPi rev 2 et +, le bus est le le 1
				else:
					bus = 2 # Si pcduino, le bus est le 2
		self.i2c_time_error = time.time()	# heure de la dernière erreur
		self.i2c_error = False
		self.addr0 = addr
		self.bus = bus
		self.device = i2c_device(addr, bus)
	
	@staticmethod
	def unError(fonction):
		'''Decorateur pour eviter les erreurs
		Si erreur dans une des methodes, on essaye de reconnecter le device 1 fois
		Si ca ne passe toujours pas, on abandonne'''
		@functools.wraps(fonction) # ca sert pour avoir un help(lcd_i2c_io) utile
		def lcd_i2c_UnErrorFonction(self,*args, **kwargs):
			if self.i2c_error:
				self.i2c_update()
			try:
				return fonction(self,*args, **kwargs)
			except IOError: 
				self.i2c_update()
				try:
					return fonction(self,*args, **kwargs)
				except IOError:
					self.i2c_error = True
		return lcd_i2c_UnErrorFonction	
	
	def i2c_update(self):
		'''Fonction qui se lance quand la connection au device plante
		'''
		if time.time()>self.i2c_time_error + i2c_device_io.timeRetry:	#On ne reconnecte pas si dernier essai trop rapproché
			self.i2c_time_error = time.time()
			try:
				self.update()
				self.i2c_error = False
			except IOError:
				self.i2c_error = True
				
	def update(self):
		''' Fonction de mise à jour de la connection
				peut être surchargée par héritage
		'''
		self.device = i2c_device(self.addr0, self.bus)

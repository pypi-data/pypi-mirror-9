#!/usr/bin/env python
# -*- coding:utf-8 -*

import functools
import time
from lcd_io import *
from i2c_device_io import *

#TODO : peut-être est-il possible de piloter le Backlight via i2c, mais n'ayant pas trouvé, pilotage via sortie digitale

class lcd_i2c_io(lcd_io, i2c_device_io):
	""" Ecran LCD branché en série i2C
			Utilise smbus
	"""
	En = 0b00000100 # Enable bit : 0x04
	Rw = 0b00000010 # Read/Write bit : 0x02
	Rs = 0b00000001 # Register select bit 0x01
	
	def __init__(self, bus=None, addr=None, pc = None, pin_bl = None, width = 16, lines = 2):
		"""Initialisation
			bus : n° du bus (defaut 1 pour RPi et 2 pour pcduino (mais il faut préciser pc))
			addr = adresse i2c de l'écran ( pour detecter : i2cdetect -y no_bus)
			pc : rpiduino_io
			pin_bl	: pin_io digital pour pilotage backlight
			width = largeur de l'écran
			lines : nb de lignes
		"""
		i2c_device_io.__init__(self, bus, addr, pc)
		self.pin_bl = pin_bl
		lcd_io.__init__(self, width, lines)
	
	def update(self):
		'''Fonction qui se lance quand la connection au device plante
		'''
		i2c_device_io.update(self)	#Mise à jour de l'i2c
		lcd_io.__init__(self, self.width, self.lines)	#Initialisation de l'écran
		
	def strobe(self, data):
		self.device.write_cmd(data | lcd_i2c_io.En | lcd_io.arg_backlight_on)
		time.sleep(.0005)
		self.device.write_cmd(((data & ~lcd_i2c_io.En) | lcd_io.arg_backlight_on))
		time.sleep(.0001)
	
	def send4bits(self, data):
		"""Envoie 4 bits au LCD
		"""
		self.device.write_cmd(data | lcd_io.arg_backlight_on)
		self.strobe(data)
	
	@i2c_device_io.unError
	def send(self, bits, mode=0, delay = False):
		""" Envoie un octet
			mode :  True pour les caractere
					False pour une commande
			delay : temps d'attente en fin de send (pour clear())			
		"""
		self.send4bits(mode | (bits & 0xF0))
		self.send4bits(mode | ((bits << 4) & 0xF0))
		if delay:
			time.sleep(delay)

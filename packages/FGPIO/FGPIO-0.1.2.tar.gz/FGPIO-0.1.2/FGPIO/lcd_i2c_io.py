#!/usr/bin/env python
# -*- coding:utf-8 -*

import i2c_lib
import functools
from time import *
from lcd_io import *

#TODO : peut-être est-il possible de piloter le Backlight via i2c, mais n'ayant pas trouvé, pilotage via sortie digitale

class lcd_i2c_io(lcd_io):
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
			pc : rpiduino_io
			pin_bl	: pin_io digital pour pilotage backlight
			width = largeur de l'écran
			lines : nb de lignes
		"""
		if bus==None:
			if pc==None:
				raise rpiduino_io_error('Lcd_i2c_io Error : bus ou pc requis.')
			else:
				if isinstance(pc, rpi_io):
					bus = 1 # Si RPi , le bus est le le 1
				else:
					bus = 2 # Si pcduino, le bus est le 2
		self.error = time.time()	# heure de la dernière erreur
		self.addr0 = addr
		self.bus = bus
		self.lcd_device = i2c_lib.i2c_device(addr, bus)
		self.pin_bl = pin_bl
		lcd_io.__init__(self, width, lines)
		
	
	def unError(fonction):
		'''Decorateur pour eviter les erreurs
		Si erreur dans une des methodes, on essaye de reconnecter le device 1 fois
		Si ca ne passe toujours pas, on abandonne'''
		@functools.wraps(fonction) # ca sert pour avoir un help(lcd_i2c_io) utile
		def lcd_i2c_UnErrorFonction(self,*args, **kwargs):
			try:
				return fonction(self,*args, **kwargs)
			except :
				self.update()
				try:
					return fonction(self,*args, **kwargs)
				except:
					pass
		return lcd_i2c_UnErrorFonction	
	
	def update(self):
		'''Fonction qui se lance quand la connection au device plante
		'''
		if time.time()>self.error+3:
			try:
				self.lcd_device = i2c_lib.i2c_device(self.addr0, self.bus)
				lcd_io.__init__(self, self.width, self.lines)
			except:
				self.error = time.time()
		
	def strobe(self, data):
		self.lcd_device.write_cmd(data | lcd_i2c_io.En | lcd_io.arg_backlight_on)
		sleep(.0005)
		self.lcd_device.write_cmd(((data & ~lcd_i2c_io.En) | lcd_io.arg_backlight_on))
		sleep(.0001)
	
	def send4bits(self, data):
		"""Envoie 4 bits au LCD
		"""
		self.lcd_device.write_cmd(data | lcd_io.arg_backlight_on)
		self.strobe(data)
	
	@unError
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

#!/usr/bin/env python
# -*- coding:utf-8 -*

"""
Gestion des modules à base de PCA9555
	comme le DFROBOT DFR0013
	
	pour extention du nd de GPIO
	sur un rpiduino_io
	- Rpi
	- pcduino

 AUTEUR : FredThx

 Projet : rpiduino_io

"""

from rpiduino_io import *
from pin_ext_io import *
from i2c_ext_io import *

INPUT = 0
OUTPUT = 1
PULLUP = 8
SERIAL = 40
I2C = 42
SPI = 41
HIGH = 1
LOW = 0


class pca9555_io(i2c_ext_io):
	"""Classe décrivant un module i2c basé sur PCA9555
			pour expension des GPIO via i2c
	"""
	
	INPUT_PORT = [0x00, 0x01]	# Pour lecture des GPIO
	OUTPUT_PORT = [0x02, 0x03]	# Pour ecriture des GPIO
	POL_INVERT = [0x04, 0x05]	# Pour inversion (1 = Invert, 0 = normal)
	CONF_IO = [0x06, 0x07]	# COnfiguration des GPIO : 1 = INPUT, 0 = OUTPUT
	
	def __init__(self, bus=None, addr=None, pc = None):
		"""Initialisation
			bus : n° du bus (defaut 1 pour RPi et 2 pour pcduino (mais il faut préciser pc))
			addr = adresse i2c du module ( pour detecter : i2cdetect -y no_bus)
			pc : rpiduino_io
		"""
		i2c_ext_io.__init__(self, bus, addr, pc, 16)	#16bits
	
	@i2c_device_io.unError
	def setmode_pin(self, id, mode):
		"""Definit le mode d'une pin
			-	INPUT
			-	OUTPUT
		"""
		reg_iodir = pca9555_io.CONF_IO[int(id/8)]
		id = id % 8
		if mode == OUTPUT:
			self.write_bit_register(reg_iodir, id, LOW)
		else:
			self.write_bit_register(reg_iodir, id, HIGH)
	
	@i2c_device_io.unError	
	def getmode_pin(self, id):
		""" Renvoie le mode d'une pin
		"""
		reg_iodir = pca9555_io.CONF_IO[int(id/8)]
		id = id % 8
		if self.read_bit_register(reg_iodir, id): # Si le mode io est INPUT (1)
			return INPUT
		else:
			return OUTPUT
	
	@i2c_device_io.unError
	def set_pin(self, id, val):
		"""Assigne la sortie id
		"""
		assert (self.getmode_pin(id) == OUTPUT), "Erreur, la pin doit être OUTPUT."
		self.write_bit_register(pca9555_io.OUTPUT_PORT[int(id/8)], id % 8, val)
	
	@i2c_device_io.unError
	def get_pin(self,id):
		"""Renvoie la valeur de la pin
		"""
		return self.read_bit_register(pca9555_io.INPUT_PORT[int(id/8)], id % 8)
		
		

#########################################################
#                                                       #
#		EXEMPLE                                         #
#                                                       #
#########################################################

if __name__ == '__main__':
	from bt_io import *
	from led_io import *
	import time
	pc = rpiduino_io()
	io_ext = pca9555_io(pc=pc)	# Si le mcp est seul sur le bus, sinon mettre l'addresse
	led = led_io(io_ext.pin[0])
	print io_ext.pin[0]
	bt = bt_io(io_ext.pin[8])
	while not bt.is_pressed:
		led.invert()
		time.sleep(0.5)
	print "ok"
		

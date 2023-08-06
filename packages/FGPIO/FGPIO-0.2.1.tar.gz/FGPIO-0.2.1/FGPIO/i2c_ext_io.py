#!/usr/bin/env python
# -*- coding:utf-8 -*

"""
 Classe 
	Module i2c pour extention des GPIO

	sur un rpiduino_io
		- Rpi
		- pcduino

 AUTEUR : FredThx

 Projet : rpiduino_io

"""

from i2c_device_io import *
from pin_ext_io import *


class i2c_ext_io(i2c_device_io):
	'''Module i2c pour extention des GPIO
	'''
	def __init__(self, bus=None, addr=None, pc = None, nb_bits = 16):
		"""Initialisation
			bus 	:	n° du bus (defaut 1 pour RPi et 2 pour pcduino (mais il faut préciser pc))
			addr 	:	adresse i2c du module ( pour detecter : i2cdetect -y no_bus)
			pc 		:	rpiduino_io
			nb_bits	:	nombre de bits
		"""
		i2c_device_io.__init__(self, bus, addr, pc)
		self.pin = []
		#Création des pins
		for i in range(0, nb_bits-1):
			self.pin.append(pin_ext_io(i, self))
		#Initialisation des pins
		for pin in self.pin:
			pin.setmode(OUTPUT)
			pin.set(LOW)
	
	def write_bit_register(self, register, no_bit, value):
		'''Ecrit une valeur dans un bit d'un registre
				register	:	adresse du registre (ex : 0x02)
				nb_bits		:	indice du bit (de 0 à 7)
				value		: 	0 ou 1
		'''
		register_values = self.device.read_data(register)
		if value:
			register_values |= 1<<no_bit	# met à 1 le id-eme bit
		else:
			register_values &= ~(1<<no_bit)	# met à 0 le id-eme bit
		self.device.write_cmd_arg(register, register_values)
	
	def read_bit_register(self, register, no_bit):
		'''Renvoie la valeur d'un bit d'un registre
				register	:	adresse du registre (ex : 0x02)
				nb_bits		:	indice du bit (de 0 à 7)
		'''
		register_values = self.device.read_data(register)
		return int((register_values & (1<<no_bit)) > 0)

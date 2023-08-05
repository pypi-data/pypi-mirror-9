#!/usr/bin/env python
# -*- coding:utf-8 -*

####################################
"""
# Gestion des modules MPC23017
#	pour extention du nd de GPIO
#	sur un rpiduino_io
#		- Rpi
#		- pcduino
#
# AUTEUR : FredThx
#
# Projet : rpiduino_io
#
"""
#################################### 

from i2c_io import *
from rpiduino_io import *
from pin_mcp_io import *

INPUT = 0
OUTPUT = 1
PULLUP = 8
SERIAL = 40
I2C = 42
SPI = 41
HIGH = 1
LOW = 0

#TODO : créer une classe i2c_device_io au dessus de cette classe et de lcd_i2c_io (en commun le décorateur @unError)
#TODO : gérer aussi la version 8 bits => héritage!
#TODO : créer des methodes qui modifient/get en masse les pins (16 bits)
#TODO : utiliser les modes interruption (si intéret)

class mcp23017_io(device_io):
	"""Classe décrivant un module MPC23017
			pour expension des GPIO via i2c
	"""
	IODIR = [0x00, 0x01]	# I/O DIRECTION REGISTER (permet de définir le sens (1=INPUT / 0=OUTPUT)
	IPOL = [0x02, 0x03]		# INPUT POLARITY REGISTER (permet d'inverser les entrees)
	GPINTEN = [0x04, 0x05]	# INTERRUPT-ON-CHANGE CONTROL REGISTER (permet de définir si une pin est définit pour interupt_on_change. Voir DEFVAL et INTCON)
	DEFVAL = [0x06, 0x07]	# DEFAULT COMPARE REGISTER FOR INTERRUPT-ON-CHANGE (permet de definir la valeur par defaut. Son opposé va générer interupt_on_change. Voir GPINTEN et INTCON)
	INTCON = [0x08, 0x09]	# INTERRUPT CONTROL REGISTER (Definit le mode de comparaison pour interupte_on_change. Si 1 : comparé à la valeur dans DEFVAL. Si 0 : comparé à la valeur précédente)
	IOCON = [0x0A, 0x0B]	# CONFIGURATION REGISTER
	GPPU = [0x0C, 0x0D]		# PULL-UP RESISTOR CONFIGURATION REGISTER ( 1 : Pull_up resistor is enable)
	INTF = [0x0E, 0x0F]		# INTERRUPT FLAG REGISTER
	INTCAPA = [0x10, 0x11]	# INTERRUPT CAPTURE REGISTER
	GPIO = [0x12, 0x13]		# PORT REGISTER (lecture ou ecriture de l'état du GPIO)
	OLAT = [0x14, 0x15]		# OUTPUT LATCH REGISTER (OLAT)
	
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
		self.error = time.time()	# heure de la dernière erreur
		self.addr0 = addr
		self.bus = bus
		self.device = i2c_device(addr, bus)	
		self.pin = []
		for i in range(0, 15):
			self.pin.append(pin_mcp_io(i, self))
		#Initialisation des pins à 0
		for pin in self.pin:
			pin.setmode(OUTPUT)
			pin.set(LOW)
		
	
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
		if time.time()>self.error+3:	#On ne reconnecte pas si dernier essai < 3 secondes
			try:
				self.device = i2c_device(self.addr0, self.bus)
			except:
				self.error = time.time()
	
	@unError
	def setmode_pin(self, id, mode):
		"""Definit le mode d'une pin
			-	INPUT
			-	OUTPUT
			-	PULLUP (INPUT with pullup resistor)
		"""
		reg_iodir = mcp23017_io.IODIR[int(id/8)]	# Registre des direction I/O (selon GPA ou GPB) : 1 = INPUT
		reg_gppu = mcp23017_io.GPPU[int(id/8)] # Registre des pullup (selon GPA ou GPB) : 1 = pullup
		id = id % 8
		iodir = self.device.read_data(reg_iodir)
		gppu =  self.device.read_data(reg_gppu)
		if mode == OUTPUT:
			iodir &= ~(1<<id)	# met à 0 le id-eme bit
			gppu &= ~(1<<id)
		else:
			iodir |= 1<<id	# met à 1 le id-eme bit
			if mode == PULLUP:
				gppu |= 1<<id
			else:
				gppu &= ~(1<<id)
		self.device.write_cmd_arg(reg_iodir, iodir)
		self.device.write_cmd_arg(reg_gppu, gppu)
	
	@unError	
	def getmode_pin(self, id):
		""" Renvoie le mode d'une pin
		"""
		reg_iodir = mcp23017_io.IODIR[int(id/8)]	# Registre des direction I/O (selon GPA ou GPB) : 1 = INPUT
		reg_gppu = mcp23017_io.GPPU[int(id/8)] # Registre des pullup (selon GPA ou GPB) : 1 = pullup
		id = id % 8
		iodir = self.device.read_data(reg_iodir)
		gppu =  self.device.read_data(reg_gppu)
		if iodir & (1<<id): # Si le mode io est INPUT (1)
			return INPUT
		else:
			if gppu & (1<<id) : # Si le mode pullup est à 1
				return PULLUP
			else:
				return OUTPUT
	
	@unError
	def set_pin(self, id, val):
		"""Assigne la sortie id
		"""
		assert (self.getmode_pin(id) == OUTPUT), "Erreur, la pin doit être OUTPUT."
		reg_gpio = mcp23017_io.GPIO[int(id/8)]	# Registre des GPIO
		id = id % 8
		gpio = self.device.read_data(reg_gpio)
		if val:
			gpio |= 1<<id
		else:
			gpio &= ~(1<<id)
		self.device.write_cmd_arg(reg_gpio, gpio)
		
	@unError
	def get_pin(self,id):
		"""Renvoie la valeur de la pin
		"""
		reg_gpio = mcp23017_io.GPIO[int(id/8)] # Registre des GPIO
		id = id % 8
		gpio = self.device.read_data(reg_gpio)
		return int((gpio & (1<<id)) > 0)
		
		

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
mcp = mcp23017_io(pc=pc)	# Si le mcp est seul sur le bus, sinon mettre l'addresse
led = led_io(mcp.pin[0])
print mcp.pin[0]
bt = bt_io(mcp.pin[8])
while not bt.is_pressed:
	led.invert()
	time.sleep(0.5)
print "ok"
		
	
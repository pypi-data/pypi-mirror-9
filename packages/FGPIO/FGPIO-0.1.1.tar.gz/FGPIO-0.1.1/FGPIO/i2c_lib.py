#!/usr/bin/env python
# -*- coding:utf-8 -*


####################################
'''
# Gestion de composants i2c
#			basée sur la lib smbus
#
# AUTEUR : FredThx
#
# Projet : rpiduino_io
#
'''
####################################


import smbus
from time import *

class i2c_device:
	""" Composant i2c
	"""
	def __init__(self, addr, port=1):
		"""Initialise le composant i2c
			addr : adresse (exemple : 0x20) Si addr==None, on scan le bus et choisit le premier qui repond
			bus : n° du bus (1,2,...)
		"""
		self.bus = i2c_bus(port)
		if addr==None:
			addrs = self.bus.scan()
			if len(addrs)>0:
				addr = self.bus.scan()[0]
			else:
				raise i2c_error('Aucun composant i2c trouvé sur le bus '+str(port))
		self.addr = addr

# Write a single command
	def write_cmd(self, cmd):
		self.bus.smbus.write_byte(self.addr, cmd)
		sleep(0.0001)

# Write a command and argument
	def write_cmd_arg(self, cmd, data):
		self.bus.smbus.write_byte_data(self.addr, cmd, data)
		sleep(0.0001)

# Write a block of data
	def write_block_data(self, cmd, data):
		self.bus.smbus.write_block_data(self.addr, cmd, data)
		sleep(0.0001)


# Read a single byte
	def read(self):
		return self.bus.smbus.read_byte(self.addr)

# Read
	def read_data(self, cmd):
		return self.bus.smbus.read_byte_data(self.addr, cmd)

# Read a block of data
def read_block_data(self, cmd):
	return self.bus.smbus.read_block_data(self.addr, cmd)

class i2c_bus(): # Je n'arrive pas à la faire héritée de smbus.SMBus!!!!!
	"""Bus i2c"""
	def __init__(self, port):
		"""Initialisation
		"""
		self.smbus = smbus.SMBus(port) # La solution est alors l'agrégation 
	def scan(self):
		"""Scan le bus et renvoie la liste des adress valides
		"""
		liste=[]
		for addr in range(0x03, 0x77):
			try:
				self.smbus.write_quick(addr)
			except:
				pass
			else:
				liste.append(addr)
		return liste
		
################################
#                              #
#    GESTION DES ERREURS       #
#                              #
################################
		
class i2c_error(Exception):
	def __init__(self, message):
		self.message = message
	def __str__(self):
		return self.message
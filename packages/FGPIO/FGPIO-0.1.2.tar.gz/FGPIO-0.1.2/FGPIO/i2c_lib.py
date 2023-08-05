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
	def __init__(self, addr=None, port=1):
		"""Initialise le composant i2c
			addr : adresse (exemple : 0x20) Si addr==None, on scan le bus et choisit le premier qui repond
			bus : n° du bus (1,2,...)
		"""
		self.bus = i2c_bus(port)
		if addr==None:	# Si l'adresse sur le bus n'est pas fournit, recherche ...
			addrs = self.bus.scan()
			if len(addrs)>0:
				self.addr = addrs[0]
	
	
	def write_cmd(self, cmd):
		''' Write a single command
		'''
		self.bus.smbus.write_byte(self.addr, cmd)
		sleep(0.0001)
	
	
	def write_cmd_arg(self, cmd, data):
		''' Write a command and argument
		'''
		self.bus.smbus.write_byte_data(self.addr, cmd, data)
		sleep(0.0001)
	
	
	def write_block_data(self, cmd, data):
		''' Write a block of data
		'''
		self.bus.smbus.write_block_data(self.addr, cmd, data)
		sleep(0.0001)
	
	
	def read(self):
		''' Read a single byte
		'''
		return self.bus.smbus.read_byte(self.addr)
	
	
	def read_data(self, cmd):
		''' Read
		'''
		return self.bus.smbus.read_byte_data(self.addr, cmd)
	
	
	def read_block_data(self, cmd):
		''' Read a block of data
		'''
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
#!/usr/bin/env python
# -*- coding:utf-8 -*

####################################
'''
 Utilisation d'un bouton rotatif à 5 pins
	ex : http://www.adafruit.com/products/377

	Classe : 	- bt_rotatif_io			:	vrai bouton rotatif
				- bt_pseudo_rotatif_io	:	simulation avec 3 bouton poussoirs
	
 AUTEUR : FredThx

 Projet : rpiduino_io
 

'''
#################################### 

#TODO : Optimiser la fonction read() : utilise trop la CPU

from rpiduino_io import *
from bt_io import *

class bt_rot_io(bt_io):
	''' Bouton rotatif
			Soit réel	:	bt_rotatif_io
			Soit pseudo	:	bt_pseudo_rotatif_io
	'''
	def __init__(self, pin_sw=None, value = 0):
		self.pin_sw = pin_sw
		if self.pin_sw != None:
			bt_io.__init__(self, pin_sw)
		self.value = value
	
	def read_value(self):
		""" renvoie la valeur cumulée
				pour initialiser : self.value = 0
		"""
		self.value += self.read()
		return self.value
	
	def set_value(self, value):
		self.value = value

class bt_rotatif_io(bt_rot_io):
	''' Bouton rotatif à 5 pins
		Branchements :
			d'un coté :
				- 0 V
				- pin_sw
			de l'autre :
				- pin_a
				- 0 V
				- pin_b
	'''
	def __init__(self, pin_a, pin_b, pin_sw=None, value = 0):
		'''Initialisation
			- pin_a		:	
			- pin_a		:	
			- pin_sw	:	pin pour intérupteur (facultatif)
			- value 	:	valeur initiale (pour comptage)
		'''
		self.pin_a = pin_a
		self.pin_b = pin_b
		self.pin_a.setmode(PULLUP)
		self.pin_b.setmode(PULLUP)
		self.lasts_read = [0,0,0,0]
		bt_rot_io.__init__(self, pin_sw, value)
	
	# Quand on tourne d'un cran, 
	#	Clockwise :	pin_a	pin_b	value
	#				1		0		0b10
	#				0		0		0b00
	#				0		1		0b01
	#				1		1		0b11
	#	trigo :
	#				0		1		0b01
	#				0		0		0b00
	#				1		0		0b10
	#				1		1		0b11
	def _read(self):
		return self.pin_a.get() | self.pin_b.get()<<1
	
	def read(self):
		""" Renvoie 
			+1 si le bouton est tourné à droite
			-1 si le bouton est tourné à gauche
			0 sinon
		"""
		value = self._read()
		if self.lasts_read[3]==value:
			return 0
		else:
			self.lasts_read.append(value)
			del self.lasts_read[0]
			if self.lasts_read==[0b10,0b00,0b01,0b11]:
				return -1
			elif self.lasts_read==[0b01,0b00,0b10,0b11]:
				return 1
			else:
				return 0

class bt_pseudo_rotatif_io(bt_rot_io):
	""" Pseudo bouton rotatif
			simulé à partir de 3 boutons poussoirs
	"""
	def __init__(self, pin_plus, pin_moins, pin_sw=None, value = 0):
		"""Initialisation
				- pin_plus	:	pin_io du bouton poussoir +
				- pin_moins	:	pin_io du bouton poussoir -
				- pin_sw 	:	pin_io du bouton de validation (facultatif)
		"""
		self.bt_plus = bt_io(pin_plus)
		self.bt_moins = bt_io(pin_moins)
		bt_rot_io.__init__(self, pin_sw, value)
		
	def read(self):
		""" Renvoie 
			+1 si le bouton plus est appuyé
			-1 si le bouton moins est appuyé
			0 si aucun ou les deux sont appuyés
		"""
		value = 0
		if self.bt_plus.is_pushed():
			value+=1
		if self.bt_moins.is_pushed():
			value-=1
		return value
		
				
				
		
#########################################################
#                                                       #
#		EXEMPLE                                         #
#                                                       #
#########################################################

if __name__ == '__main__':
	import time
	pc = rpiduino_io()
	bt = bt_rotatif_io(*pc.logical_pins(9,10,13))
	#bt = bt_pseudo_rotatif_io(*pc.logical_pins(11,12,8))
	print "Appuyer sur le bouton"
	while not bt.is_pushed():
		pass
	print"Tourner maintenant"
	while not bt.is_pushed():
		print bt.read_value()
	print "Ok."
		
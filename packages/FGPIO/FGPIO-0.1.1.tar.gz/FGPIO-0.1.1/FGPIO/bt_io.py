#!/usr/bin/env python
# -*- coding:utf-8 -*

####################################
"""
# Bouton branchée sur un rpi_duino_io
# 
#	Cablage :	une broche du bouton sur le 0V
#				l'autre sur une entrée numérique
#
# AUTEUR : FredThx
#
# Projet : rpiduino_io
#
"""
#################################### 


from rpiduino_io import *

class bt_io(device_io):
	''' Bouton branchée sur un rpiduino (pcduino ou Rpi)
	'''
	def __init__(self, pin):
		''' Initialisation
				pin	:	digital_pin_io
		'''
		if isinstance(pin, digital_pin_io):
			self.pin = pin
			self.pin.setmode(PULLUP) # c'est à dire avec une résistance interne placée entre la pin et le +3.3V pour remettre à HIGH la pin quand non branchée
		else:
			raise rpiduino_io_error('argument erreur : n''est pas du type digital_pin_io')
	
	def get(self):
		''' Récupère l'état du bouton sous la forme LOW/HIGH
		'''
		return self.pin.get()
	
	@property
	def is_pressed(self):
		''' renvoie True si le bouton est pressé. False sinon
		'''
		return (self.pin.get()==LOW)

#########################################################
#                                                       #
#		EXEMPLE                                         #
#                                                       #
#########################################################

if __name__ == '__main__':
	import time
	pc = rpiduino_io()
	pin = pc.logical_pin(2)
	bt = bt_io(pin)
	print "Appuyer sur le bouton"
	while not bt.is_pressed:
		time.sleep(0.1)
	print "Ok."
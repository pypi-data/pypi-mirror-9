#!/usr/bin/env python
# -*- coding:utf-8 -*

####################################
'''
# LED branchée sur un rpi_duino_io
# 
#    C'est vraiment pour faire jolie cette classe!!!
#
# AUTEUR : FredThx
#
# Projet : rpiduino_io
#
'''
#################################### 


from rpiduino_io import *

class led_io (device_io):
	''' LED branchée sur un rpiduino (pcduino ou Rpi)
	'''
	def __init__(self, pin):
		''' Initialisation
				pin	:	digital_pin_io
		'''
		if isinstance(pin, digital_pin_io):
			self.pin = pin
			self.pin.setmode(OUTPUT)
		else:
			raise rpiduino_io_error('argument erreur : n''est pas du type digital_pin_io')
	
	def set(self, etat):
		''' change l'état de la LED
			etat	:	False / True
		'''
		if etat:
			self.pin.set(HIGH)
		else:
			self.pin.set(LOW)
	
	def get(self):
		''' Récupère l'état de la LED
		'''
		return self.pin.get()
	
	def on(self):
		''' Allume la LED
		'''
		self.set(True)
	
	def off(self):
		''' Eteint la LED
		'''
		self.set(False)
	
	def invert(self):
		'''Cumutte la LED
		'''
		self.pin.invert()
	
		
#########################################################
#                                                       #
#		EXEMPLE                                         #
#                                                       #
#########################################################

if __name__ == '__main__':
	import time
	pc = rpiduino_io()
	pin = pc.pin[2]
	LED = led_io(pin)
	LED.on()
	time.sleep(1)
	LED.off()
	time.sleep(1)
	while True:
		LED.invert()
		print "la LED est " + str(LED.get())
		time.sleep(1)
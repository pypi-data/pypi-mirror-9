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
	def __init__(self, pin=None):
		''' Initialisation
				pin	:	digital_pin_io
						(is None ou omis, la led est innactive
		'''
		if pin==None:
			self.pin = None
		else:
			if isinstance(pin, digital_pin_io):
				self.pin = pin
				self.pin.setmode(OUTPUT)
			else:
				raise rpiduino_io_error('argument erreur : n''est pas du type digital_pin_io')
	
		
	def none_none(fonction):
		'''Décorateur : si pin==None : la fonction ne s'applique pas
		'''
		def none_none_fonction(self, *args, **kwargs):
			if self.pin == None:
				return None
			else:
				return fonction(self, *args, **kwargs)
		return none_none_fonction
			
	@none_none
	def set(self, etat):
		''' change l'état de la LED
			etat	:	False / True
		'''
		if etat:
			self.pin.set(HIGH)
		else:
			self.pin.set(LOW)
	
	@none_none
	def get(self):
		''' Récupère l'état de la LED
		'''
		return self.pin.get()
	
	@none_none
	def on(self):
		''' Allume la LED
		'''
		self.set(True)
	
	@none_none
	def off(self):
		''' Eteint la LED
		'''
		self.set(False)
	
	@none_none
	def invert(self):
		'''Comutte la LED
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
	none_led = led_io()
	LED.on()
	none_led.on() # Ne fait rien!
	time.sleep(1)
	LED.off()
	time.sleep(1)
	while True:
		LED.invert()
		print "la LED est " + str(LED.get())
		time.sleep(1)
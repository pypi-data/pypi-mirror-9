#!/usr/bin/env python
# -*- coding:utf-8 -*

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


from rpiduino_io import *

class bt_io(digital_input_device_io):
	''' Bouton poussoir branchée sur un rpiduino (pcduino ou Rpi)
	'''
	def __init__(self, pin, thread = False, on_changed = None, pause = 0.1):
		''' Initialisation
				- pin		:	digital_pin_io
				- thread	:	(facultatif) True si utilisation thread
				- on_changed:	deamon quand le capteur change
				- pause		:	pause entre chaque lecture du composant
		'''
		if isinstance(pin, digital_pin_io):
			self.pin = pin
			self.pin.setmode(PULLUP) # c'est à dire avec une résistance interne placée entre la pin et le +3.3V pour remettre à HIGH la pin quand non branchée
		else:
			raise rpiduino_io_error('argument erreur : n''est pas du type digital_pin_io')
		self.last_state= False
		digital_input_device_io.__init__(self, thread, on_changed, pause)
	
	def get(self):
		''' Récupère l'état du bouton sous la forme LOW/HIGH
		'''
		return self.pin.get()
	
	@property
	def is_pressed(self):
		''' renvoie True si le bouton est pressé. False sinon
		'''
		return (self.pin.get()==LOW)
	
	def is_pushed(self):
		''' renvoie true si le bouton devient appuyé
			(s'il reste appuyé, renvoie False)
		'''
		value = self.is_pressed
		if self.last_state == value:
			return False
		else:
			self.last_state = value
			return value
	
	def read(self):
		''' Lecture, pour le thread, du bouton
		'''
		return self.is_pressed
		
#########################################################
#                                                       #
#		EXEMPLE                                         #
#                                                       #
#########################################################

if __name__ == '__main__':
	import time
	pc = rpiduino_io()
	bt = bt_io(pc.logical_pin(8))
	def action_bt_change():
		if bt2.th_readed():
			print "bt2 Pushed."
		else:
			print "bt2 Released."
	bt2 = bt_io(pc.logical_pin(10), True, action_bt_change)
	
	try: #Ca permet de pouvoir planter le thread avec un CTRL-C
		print "Appuyer sur les boutons"
		while True:
			if bt.is_pushed():
				print "Bt est appuyé"
			time.sleep(0.1)
	except KeyboardInterrupt:
		bt2.stop()
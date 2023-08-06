#!/usr/bin/env python
# -*- coding:utf-8 -*

"""
	Gestion des prises radio commandés en 434Mhz
"""


from rcSwitch_io import *
import time

class prise:
	"""prise radio commandée
	"""
	def __init__(self, rcSwitch, code, prise_id, nom = ''):
		"""Prise de courant radio commandée en 434Mhz
			ex: SMART HOME ref YC-4000B
			
				- rcSwitch	:	rcSwitch_io
								(ex : rcSwitchio(*rpiduino().logical_pins(2))
				- code		:	code du groupe de prises (ex : '00010')
				- prise_id	:	code de la prise (ex : '1000' pour la prise A)
				- nom (faculatif)
		"""
		self.rcSwitch = rcSwitch
		self.code = code
		self.prise_id = prise_id
		self.nom = nom
	
	def setON(self):
		self.rcSwitch.sendOrder(self.code, self.prise_id, 1)
	def setOFF(self):
		self.rcSwitch.sendOrder(self.code, self.prise_id, 0)

# Exemple		

if __name__ == '__main__':
	pc = rpiduino_io()
	rcSwitch = rcSwitch_io(*pc.logical_pins(2))
	A = prise(rcSwitch,'00010', '10000')
	B = prise(rcSwitch,'00010', '01000')
	C = prise(rcSwitch,'00010', '00100')
	D = prise(rcSwitch,'00010', '00010')
	A.setON()
	B.setON()
	C.setON()
	D.setON()
	time.sleep(2)
	A.setOFF()
	B.setOFF()
	C.setOFF()
	D.setOFF()

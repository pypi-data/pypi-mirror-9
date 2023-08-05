#!/usr/bin/env python
# -*- coding:utf-8 -*

####################################
'''
# 1602A LCD 
# (ou HD4478 mais non testé) 
# branché en parallèle
#
# AUTEUR : FredThx
#
# Projet : rpiduino_io
#
'''
#################################### 

 
import time
from lcd_io import *

class lcd_lpt_io(lcd_io):
	""" Ecran LCD HD44780 branché en parallèle
	Branchement :
			1 : GND
			2 : 5V
			3 : Contrast (0-5V) (mettre pin centre potentiometre , les deux autres pins sur 0V et 5V)
			4 : RS (Register Select)	(pin_rs)
			5 : R/W (Read Write)       - mettre sur 0V
			6 : Enable or Strobe		(pin_e)
			7 : Data Bit 0             - NOT USED
			8 : Data Bit 1             - NOT USED
			9 : Data Bit 2             - NOT USED
			10: Data Bit 3             - NOT USED
			11: Data Bit 4				(pin_d4)
			12: Data Bit 5				(pin_d5)
			13: Data Bit 6				(pin_d6)
			14: Data Bit 7				(pin_d7)
			15: LCD Backlight +5V** ou 	(pin_bl) si on veut piloter le retro éclairage
			16: LCD Backlight GND
	"""
	
	def __init__(self, pin_rs, pin_e, pin_d4, pin_d5, pin_d6, pin_d7, pin_bl=None, width=16, lines = 2):
		""" Initialisation
			pin_rs : pin de la broche 4 du LCD
			pin_e  : pin de la broche 6 du LCD
			pin_d4 : pin de la broche 11 du LCD
			pin_d5 : pin de la broche 12 du LCD
			pin_d6 : pin de la broche 13 du LCD
			pin_d7 : pin de la broche 14 du LCD
			pin_bl : pin de la broche 15 du LCD (backlight)
			width  : max caractères par ligne
			lines  : nb de lignes
		"""
		#TODO : faire vérif de type
		#TODO : pins=[pin_d4, ...d7]
		self.pin_rs = pin_rs
		self.pin_rs.setmode(OUTPUT)
		self.pin_e = pin_e
		self.pin_e.setmode(OUTPUT)
		self.pin_d4 = pin_d4
		self.pin_d4.setmode(OUTPUT)
		self.pin_d5 = pin_d5
		self.pin_d5.setmode(OUTPUT)
		self.pin_d6 = pin_d6
		self.pin_d6.setmode(OUTPUT)
		self.pin_d7 = pin_d7
		self.pin_d7.setmode(OUTPUT)
		self.pin_bl = pin_bl
		lcd_io.__init__(self, width, lines)
	
	def send(self, bits, mode, delay = False):
		""" Envoie un octet 
			mode :  True pour les caractere
					False pour une commande
			delay : temps d'attente en fin de send (pour clear())
		"""
		self.pin_rs.set(mode)
		# High bits
		self.send4bits(bits/16)
		# Low bits
		self.send4bits(bits & 0b00001111)
		if delay:
			time.sleep(delay)
	
	def send4bits(self, bits):
		""" Envoie 4 bits au LCD
		"""
		self.pin_d4.set(LOW)
		self.pin_d5.set(LOW)
		self.pin_d6.set(LOW)
		self.pin_d7.set(LOW)
		if bits&0b0001 == 0b0001:
			self.pin_d4.set(HIGH)
		if bits&0b0010 == 0b0010:
			self.pin_d5.set(HIGH)
		if bits&0b0100 == 0b0100:
			self.pin_d6.set(HIGH)
		if bits&0b1000 == 0b1000:
			self.pin_d7.set(HIGH)
		self.pin_e.set(LOW)
		time.sleep(lcd_io.e_pulse)
		self.pin_e.set(HIGH)
		time.sleep(lcd_io.e_pulse)
		self.pin_e.set(LOW)
		time.sleep(lcd_io.e_delay)


#########################################################
#                                                       #
#		EXEMPLE                                         #
#                                                       #
#########################################################

if __name__ == '__main__':
	pc=rpiduino_io()
	if pc.modele == 'RPi':
		#lcd = lcd_lpt_io(pc.pin[22],pc.pin[24],pc.pin[16],pc.pin[8],pc.pin[26],pc.pin[10])
		#lcd = lcd_lpt_io(*pc.bmc_pins(25,8,23,14,7,15)) # syntaxe alternative avec la numérotation BMC
		lcd = lcd_lpt_io(*pc.logical_pins(6,10,4,15,11,16)) # syntaxe alternative avec la numérotation logique
	else:
		#lcd = lcd_lpt_io(pc.pin[7],pc.pin[8],pc.pin[9],pc.pin[10],pc.pin[11],pc.pin[12])
		lcd = lcd_lpt_io(*pc.physical_pins(7,8,9,10,11,12))# syntaxe alternative
	lcd.message('Hello, je suis un ' + str(pc.modele))
	
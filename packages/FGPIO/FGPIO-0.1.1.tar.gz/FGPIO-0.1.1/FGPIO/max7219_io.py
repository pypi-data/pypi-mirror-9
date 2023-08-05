#!/usr/bin/env python
# -*- coding:utf-8 -*

####################################
'''
# Pilotage module de LEDs 
#			MAX7219
#			pilotage directe, sans API SPI
#
# AUTEUR : FredThx
#
# Projet : rpiduino_io
#
'''
#################################### 

#TODO : faire d'autre modules SPI
#			soit classe et sous classes
#		_ réaliser des ronds qui grandissent, des explosions, ....
#		_ gerer d'autres fonctions (intensité, ...) voir led.py


from rpiduino_io import *
from font_io import *
import time


class max7219_io(device_io):
	""" Module à LED MAX7219
	"""
	def __init__(self, pin_din, pin_cs, pin_clk, font = font_io()):
		""" Initialisation module MAX7219
				pin_din	:	pin_io DIN
				pin_cs	:	pin_io CS
				pin_clk	:	pin_io CLK
				font	:	font_io
		"""
		self.pin_din = pin_din
		self.pin_cs = pin_cs
		self.pin_clk = pin_clk
		self.font = font
		self.pin_clk.setmode(OUTPUT)
		self.pin_cs.setmode(OUTPUT)
		self.pin_din.setmode(OUTPUT)
		time.sleep(0.1)
		self.send(0x09,0x00)
		self.send(0x0a,0x03)
		self.send(0x0b,0x07)
		self.send(0x0c,0x01)
		self.send(0x0f,0x00)
		time.sleep(0.1)
		
		
	def send_byte(self, data):
		""" Envoie un octet au module
				data	:	un caractere
		"""
		self.pin_cs.set(LOW)
		for i in range(8,0,-1):
			self.pin_clk.set(LOW)
			if (data&0x80)==0x80:
				self.pin_din.set(HIGH)
			else:
				self.pin_din.set(LOW)
			data = data<<1 # décale les bits vers la gauche
			self.pin_clk.set(HIGH)
	
	def send(self, adresse, data):
		"""  Envoie un octet au module à une adresse
		"""
		self.pin_cs.set(LOW)
		self.send_byte(adresse)
		self.send_byte(data)
		self.pin_cs.set(HIGH)
	
	def write8(self, car):
		""" Affichage de 8 octets
				car = [ligne1, ..., ligne8]
				ligne1 = 0b01010101 par exemple
		"""
		for i in range(1,9):
			self.send(i,car[i-1])
	
	def write(self, texte):
		""" Affichage d'un caractere
				texte = "F"
		"""
		texte = texte[0]
		self.write8(self.font.bits(texte))
	
	def message(self, texte, repeat = False):
		""" Ecriture d'un message et scrolling (sens pins vers le bas)
				texte	:	le message
				repeat	:	False (par defaut)
							True : indéfiniment
							entier : nb de fois
		"""
		while repeat:
			datas = self.font.bits(texte+" ")
			for i in range(0,len(datas)-7):
				self.write8(datas[i:i+8])
			if repeat is not True:
				repeat+=-1

if __name__ == '__main__':
	pc = rpiduino_io()
	font = font_io()
	font.rotate(-1)
	led = max7219_io(*pc.logical_pins(2,3,4), font=font)
	led.message("Fred est beau".upper(), 2)

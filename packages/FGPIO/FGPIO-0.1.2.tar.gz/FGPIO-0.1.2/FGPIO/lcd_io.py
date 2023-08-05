#!/usr/bin/env python
# -*- coding:utf-8 -*

####################################
"""
# Gestion des ecrans LCD avec rpiduino_io
#	Soit branché en parallele, soit en série (i2c)
#
# AUTEUR : FredThx
#
# Projet : rpiduino_io
#
"""
#################################### 

 
import time
from textwrap import wrap
from rpiduino_io import *

#TODO : initialiser un thread qui gère tout seul le scrolling
#TODO : gestion des erreurs (ligne> max), ....

class lcd_io(device_io):
	""" Ecran LCD
			classes filles:
				- lcd_lpt_io	pour les ecran connectés en pararelle (4bits)
				- lcd_i2c_io	pour les ecrans connectés en série i2c
				- lcd_spi_io	TODO
	"""
	adr_ligne = {1:0x80,2:0xC0,3:0x94,4:0xD4} #Adresses des lignes de l'écran
	e_pulse = 0.000001 # 1 µs
	e_delay = 0.00005 # 50 µs
	c_delay = 0.002 # 2 ms pour commande clear
	chr = HIGH
	cmd = LOW
	# Commandes
	cmd_clear_display = 0x01
	cmd_return_home = 0x02
	cmd_entry_model_set = 0x04
	cmd_display_control = 0x08
	cmd_cursor_shift = 0x10
	cmd_function_set = 0x20
	cmd_set_cgramaddr = 0x40
	cmd_set_ddramaddr = 0x80
	# Arguments pour entry_model_set
	arg_entry_right = 0x00
	arg_entry_left = 0x02
	arg_entry_shift_increment = 0x01
	arg_entry_shift_decrement = 0x00
	# arguments pour display on/off control
	arg_display_on = 0x04
	arg_display_off = 0x00
	arg_cursor_on = 0x02
	arg_cursor_off = 0x00
	arg_blink_on = 0x01
	arg_blink_off = 0x00
	# arguments pour display/cursor_shift
	arg_display_move = 0x08
	arg_cursor_move = 0x00
	arg_move_right = 0x00
	arg_move_left = 0x00
	# arguments pour function_set
	arg_8bit_mode = 0x10
	arg_4bit_mode = 0x00
	arg_2line = 0x08
	arg_1line = 0x00
	arg_5x10_dots = 0x04
	arg_5x8_dots = 0x00
	# arguments pour controle backlight
	arg_backlight_on = 0x08
	arg_backlight_off = 0x00
	
	
	
	
	def __init__(self, width=16, lines = 2):
		"""Initialisation
		"""
		self.width = width
		self.lines = lines
		self.send(0x33,lcd_io.cmd)		# 0b00110011	Function Set : 8bits, mode 1 ligne, 5x8 dots format mode
		self.send(0x32,lcd_io.cmd)		# 0b00110010	Idem?????
		self.send(0x28,lcd_io.cmd)		# 0b00101000	Function Set : 4 bits mode, mode 2 lignes, 5x8 dots format mode
		self.send(0x0C,lcd_io.cmd)		# 0b00001100	Display ON, Cursor OFF, Cursor blink OFF
		self.send(0x06,lcd_io.cmd)		# 0b00000110	Entry mode set : Ecriture de gauche à droite
		self.scroll_time = time.time()
		self.scroll_texte = {}					# scroll_texte = texte pour scrolling ou False
		for i in range(0,self.lines+1):			# self.txt_message[0] = texte pour scrolling multiligne
			self.scroll_texte[i] = False		# les autres, pour scrolling ligne à ligne

		self.txt_message = {}				# txt_message = le texte a afficher (pour vérif si changement de texte)
		for i in range(0,self.lines+1):		# self.txt_message[0] = texte pour multiligne
			self.txt_message[i] = ''		# les autres, pour ligne à ligne
		if self.pin_bl != None:
			self.pin_bl.setmode(OUTPUT)
			self.pin_bl.set(HIGH)
		self.clear()					# Efface l'écran
	
	def message(self, texte, ligne = False, defilement = False):
		"""Affiche le texte sur le LCD
			si ligne est omis : sur toutes les lignes
			si ligne = 1 : ligne 1
			si ligne = 2 : ligne 2
			....
			si defilement = True : scrolling possible
		"""
		if ligne != False:
			self.txt_message[0] = ''
			if self.txt_message[ligne] != texte:
				self.txt_message[ligne] = texte
				self.scroll_texte[ligne] = False
				self.send(lcd_io.adr_ligne[ligne], lcd_io.cmd)
				self.string(texte)
				# S'il faut utiliser le scrolling
				if len(texte) > self.width and defilement:
					self.scroll_texte[ligne] = texte
		
		else: #On va ecrire sur toutes les lignes
			for i in range(0, self.lines):
				self.txt_message[i+1]=''
			if self.txt_message[0] != texte:
				self.txt_message[0] = texte
				for i in range(0,self.lines+1):
					self.scroll_texte[i] = False
				lignes = wrap(texte, self.width)
				if lignes==[]:
					lignes = ['']
				if len(lignes)<= self.lines: # Si on peut sans couper les mots
					for i in range(0, len(lignes)):
						self.message(lignes[i],i+1)
				else:
					# Si ça ne rentre pas, on coupe à la hache
					for i in range(0, self.lines):
						self.message(texte[i*self.width:(i+1)*self.width-1], i+1)
					# S'il faut utiliser le scrolling
					if ((len(texte)>self.lines*self.width) and defilement):
						self.scroll_texte[0] = texte
	
	def scroll(self, delay=0.5):
		""" Fait défiler le ou les textes d'un caractere
			A utiliser "de temps en temps"
		"""
		# Si on arrive ici trop tôt, il faut patienter
		if time.time()  - self.scroll_time <delay:
			time.sleep( - time.time()  + self.scroll_time + delay)
		self.scroll_time = time.time()
		for i in range(0, self.lines+1):
			if self.scroll_texte[i]:
				texte = self.scroll_texte[i]
				long = len(texte)
				texte = texte[long-1] + texte[:long-1]
				if i == 0:
					self.message(texte,False,True)
				else:
					self.message(texte,1,True)
	
	def string(self, message):
		""" Envoie le texte au lcd
		"""
		message = message.ljust(self.width," ") #A juste au nombre de caractere par ligne
		for i in range(self.width):
			self.send(ord(message[i]),self.chr)
	
	def clear(self):
		''' Effacement de l'écran
		'''
		for i in range(0,self.lines+1):
			self.txt_message[i] = ''
		self.send(lcd_io.cmd_clear_display, lcd_io.cmd, lcd_io.c_delay)
	
	def backlight(self, mode):
		""" Eteint le retro eclairage
				mode : True (allumé)/ False(éteint)
		"""
		if self.pin_bl != None:
			if mode:
				self.pin_bl.set(HIGH)
			else:
				self.pin_bl.set(LOW)

#########################################################
#                                                       #
#		EXEMPLE                                         #
#                                                       #
#########################################################

if __name__ == '__main__':
	from lcd_lpt_io import *
	from lcd_i2c_io import *
	# Pour connection parallele 4bits
	pc=rpiduino_io()
	if pc.modele == 'RPi':
		lcd1 = lcd_lpt_io(*pc.logical_pins(6,10,4,15,11,16)) # syntaxe alternative avec la numérotation logique
	else:
		lcd1 = lcd_lpt_io(*pc.physical_pins(7,8,9,10,11,12))# syntaxe alternative
	# Pour connection i2c
	lcd2 = lcd_i2c_io(2,0x20)
	lcd1.message('Hello, je suis un ' + str(pc.modele))
	lcd2.message('Hello, je suis en i2c')
	
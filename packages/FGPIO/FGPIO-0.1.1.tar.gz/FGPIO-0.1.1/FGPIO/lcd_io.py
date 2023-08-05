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

#TODO : allumer et éteindre backlight
#		chercher un ecran % bus et adr

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
	cmd_return_home = 0x04
	cmd_entry_model_set = 0x08
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
		self.send(0x33,lcd_io.cmd)		# 0b00110011	Function Set : 8bits, mode 1 ligne, 5x8 dots format mode
		self.send(0x32,lcd_io.cmd)		# 0b00110010	Idem?????
		self.send(0x28,lcd_io.cmd)		# 0b00101000	Function Set : 4 bits mode, mode 2 lignes, 5x8 dots format mode
		self.send(0x0C,lcd_io.cmd)		# 0b00001100	Display ON, Cursor OFF, Cursor blink OFF
		self.send(0x06,lcd_io.cmd)		# 0b00000110	Entry mode set : Ecriture de gauche à droite
		self.clear()					# Efface l'écran
		self.scroll_time = time.time()
		self.scroll_texte = False
		self.scroll_texte_1 = False
		self.scroll_texte_2 = False
		
	
	def message(self, texte, ligne = False, defilement = False):
		"""Affiche le texte sur le LCD
			si ligne est omis : sur deux lignes a la suite
			si ligne = 1 : ligne 1
			si ligne = 2 : ligne 2
		"""
		#TODO : gestion de plusieurs lignes (4)
		#		possibilité de scroller sur 1 ligne
		if ligne==1:
			self.scroll_texte_1 = False
			self.send(lcd_io.adr_ligne[1], lcd_io.cmd)
			self.string(texte)
			# S'il faut utiliser le scrolling
			if len(texte) > self.width and defilement:
				self.scroll_texte_1 = texte
		
		elif ligne==2:
			self.scroll_texte_2 = False		
			self.send(lcd_io.adr_ligne[2], lcd_io.cmd)
			self.string(texte)
			# S'il faut utiliser le scrolling
			if len(texte) > self.width and defilement:
				self.scroll_texte_2 = texte
		
		else: #On va ecrire sur deux lignes
			self.scroll_texte_1 = False
			self.scroll_texte_2 = False
			lignes = wrap(texte, self.width)
			if lignes==[]:
				lignes = ['']
			if len(lignes)<3: # Si on peut sans couper les mots
				self.message(lignes[0],1)
				if len(lignes)>1:
					self.message(lignes[1],2)	
			else:
				# Si ça ne rentre pas, on coupe à la hache
				self.message(texte[:self.width],1)
				self.message(texte[self.width:],2)
				# S'il faut utiliser le scrolling
				if len(texte)>2*self.width and defilement:
					self.scroll_texte = texte
	
	def scroll(self, delay=0.5):
		""" Fait défiler le ou les textes d'un caractere
			A utiliser "de temps en temps"
		"""
		# Si on arrive ici trop tôt, il faut patienter
		while time.time() - self.scroll_time<delay:
			pass
		self.scroll_time = time.time()
		if self.scroll_texte_1:
			texte = self.scroll_texte_1
			long = len(texte)
			texte = texte[long-1] + texte[:long-1]
			self.message(texte,1,True)
		if self.scroll_texte_2:
			texte = self.scroll_texte_2
			long = len(texte)
			texte = texte[long-1] + texte[:long-1]
			self.message(texte,2,True)
		if self.scroll_texte:
			texte = self.scroll_texte
			long = len(texte)
			texte = texte[long-1] + texte[:long-1]
			self.message(texte,False,True)
	
	def string(self, message):
		""" Envoie le texte au lcd
		"""
		message = message.ljust(self.width," ") #A juste au nombre de caractere par ligne
		for i in range(self.width):
			self.send(ord(message[i]),self.chr)
	
	def clear(self):
		''' Effacement de l'écran
		'''
		self.send(lcd_io.cmd_clear_display, lcd_io.cmd, lcd_io.c_delay)
	
	def stop(self):
		'''Eteindre le backlight
		'''
		self.message("Extinction de l'écran..... TODO .....",False, True)

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
	
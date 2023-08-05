#!/usr/bin/env python
# -*- coding:utf-8 -*

####################################
"""
Gestionnaire de menus
	pour rpiduino (RPi ou pcduino)
	avec LCD et bouton rotatif

 AUTEUR : FredThx

 Projet : rpiduino_io

"""
#################################### 
import time

class f_interface(object):
	''' Interface basée sur la navigation dans un menus
	'''
	def __init__(self, lcd, bt, menu, timeout=None):
		'''Initialisation
			- lcd	:	lcd_io
			- bt	:	rotary_encoder_io
			- menu	:	f_menu
			- timeout : sort du menu si pas d'activité après time out (secondes)
		'''
		self.lcd = lcd
		self.bt = bt
		self.menu = menu # Menu en cours qui varie selon navigation
		self.menu_init = menu # Menu initial pour revenir au début
		self.timeout = timeout
		self.end_time = 0
		self.menu.addReturns() # ajout automatique des retours en bas des sous-menus
	
	def start_once(self):
		'''Execute l'interface une seule boucle
		'''
		bt_move = self.bt.read()
		if bt_move!=0:
			self.move(bt_move)
			self.show()
		if self.bt.is_pushed():
			self.action()
			self.show()
	def start(self):
		''' Execute l'interface
		'''
		self.menu = self.menu_init
		self.show()
		while self.menu != None and not self.is_timeout():
			self.start_once()
			time.sleep(0.001) # pour économiser de la CPU (si plus grand, le bouton rotatif ne marche pas bien ( à améliorer)
		
	def show(self):
		"""Affiche les elements du menu sur le lcd
		"""
		if self.menu != None:
			self.init_end_time()
			i_menus = self.menu.current_top_index
			i_lcd = 0
			while i_menus <= len(self.menu.items) and i_lcd<self.lcd.lines:
				if i_menus==self.menu.current_index:
					self.lcd.message(">" + self.menu.items[i_menus].label, i_lcd+1)
				else:
					self.lcd.message(" " + self.menu.items[i_menus].label, i_lcd+1)
				i_menus+=1
				i_lcd+=1
		else:
			self.lcd.clear()
	
	def move(self, delta):
		""" Déplace le curseur 
				si delta == 1, vers le bas
				si delta == -1, vers le haut
		"""
		if delta>0:
			if len(self.menu.items)>self.menu.current_index+delta: # S'il existe des items en dessous
				self.menu.current_index+=delta
			if self.menu.current_top_index + self.lcd.lines -2 <= self.menu.current_index : # Si on est sur la derniere ligne de l'écran ou plus bas
				if self.menu.current_top_index + delta + self.lcd.lines <= len(self.menu.items): # Si on peut descendre l'affichage
					self.menu.current_top_index+=delta
		if delta<0:
			if self.menu.current_index+delta>=0: # si on peut monter
				self.menu.current_index+=delta
			if self.menu.current_index <= self.menu.current_top_index: #Si on est sur la premiere ligne de l'écran ou plus haut
				if self.menu.current_top_index + delta >= 0: # Si on peut monter l'affichage
					self.menu.current_top_index+=delta
	
	def init_end_time(self):
		""" Initialise le timeout
		"""
		if self.timeout != None:
			self.end_time = time.time() + self.timeout
		else :
			self.end_time = time.time() + 31104000 #1an : 360*24*-60*60
			
	def is_timeout(self):
		""" Renvoie True si le timeout est dépassé
		"""
		return time.time() > self.end_time
	
	def action(self):
		""" Réalise l'action du menu
				soit sous menu
				soit sous menu dynamique
				soit commande
		"""
		#Si l'action est un SOUS-MENU
		if self.menu.current_link() == None:
			self.menu = None
		elif type(self.menu.current_link()) == f_menu:
			self.menu = self.menu.current_item().link
			if self.menu.current_item().is_retour():
				self.menu.init()
		# Si l'action est une COMMANDE
		elif type(self.menu.current_link()) == f_cmd:
			self.menu.run_current_action()
		# Si l'action est un MENU DYNAMIQUE
		elif type(self.menu.current_link()) == f_menu_dynamic:
			menu = self.menu.run_current_action()
			menu.append(f_item("Retour", self.menu, retour=True))
			self.menu = f_menu(*menu)

			
			

class f_menu(object):
	''' menu pour f_interface
	'''
	def __init__(self, *items):
		'''Initialisation
			*items : liste de menus ou commandes
		'''
		self.items = list(items)
		self.init()
	
	def init(self):
		self.current_index = 0 # Index du curseur 
		self.current_top_index = 0 # Index de la première ligne		
	
	def add(self, *items):
		''' Ajoute un ou plusieurs items
		'''
		self.items.extend(list(items))
		
	def current_item(self):
		return self.items[self.current_index]

	def current_link(self):
		return self.items[self.current_index].link
	
	def run_current_action(self):
		return self.items[self.current_index].link.run()
		
	def addReturns(self, top_menu=None):
		for item in self.items:
			if type(item.link)==f_menu:
				item.link.addReturns(self)
		if top_menu!=None:
			self.add(f_item("Retour", top_menu, retour=True))
	
		
		
class f_item(object):
	""" element d'un menu
	"""
	def __init__(self, label, link, retour=False):
		""" Initialisation
		"""
		self.label = label
		self.link = link
		self.retour = retour
	
	def is_retour(self):
		return self.retour==True

class f_cmd(object):
	""" commande
	"""
	def __init__(self, cmd, *args, **kwargs):
		"""Initialisation
			cmd		:	code à executer (soit texte, soit fonction)
			+ en option arguments (pour fonction)
		"""
		self.cmd=cmd
		self.args = args
		self.kwargs = kwargs
	
	def run(self):
		"""Execute la commande
		"""
		if type(self.cmd) is str:
			exec self.cmd
		else:
			self.cmd(*self.args, **self.kwargs)
		
class f_menu_dynamic(f_menu):
	""" Menu ou la liste des items est calculée dynamiquement
	"""
	def __init__(self, cmd, *args, **kwargs):
		"""Initialisation
				cmd		:	code qui renvoie une liste de f_item
							Soit du texte, soit une fonction
				+ en option arguments
		"""
		self.cmd = cmd
		self.args = args
		self.kwargs = kwargs
	
	def run(self):
		"""Execute le code de cmd et renvoie la liste des f_item
		"""
		if type(self.cmd) is str:
			return eval(self.cmd)
		else:
			return eval(self.cmd(*args, **kwargs))
	

#########################################################
#                                                       #
#		EXEMPLE                                         #
#                                                       #
#########################################################


if __name__ == '__main__':
	from lcd_i2c_io import *
	from rotary_encoder_io import *
	pc = rpiduino_io()
	lcd = lcd_i2c_io(pc=pc)
	bt = bt_rotatif_io(*pc.logical_pins(9,10,8))
	menu = f_menu( \
			f_item("Lecture aleatoire", f_cmd('print "lecture aléatoire"')), \
			f_item("Ma musique", f_menu( \
				f_item("Artist", f_menu_dynamic('artist()')), \
				f_item("Album", f_menu_dynamic('todo')), \
				f_item("genre", f_menu_dynamic('todo')), \
				f_item("dossier", f_menu_dynamic('todo')))), \
			f_item("Radio", f_menu( \
				f_item("France Inter",f_cmd('todo')), \
				f_item("france Info", f_cmd('todo')), \
				f_item("Recherche", f_menu_dynamic('todo')))), \
			f_item("Recherche", f_cmd('todo')), \
			f_item("Volume", f_cmd('todo')), \
			f_item("Exit", None))
	def artist():
		return [f_item("Beatles", f_cmd('print "Beatles"')), \
				f_item(time.strftime("%H:%M:%S"), f_cmd('print "Beatles"')), \
				f_item("Clash", f_cmd('print "Clash"'))]
	interface = f_interface(lcd, bt, menu)
	interface.start()
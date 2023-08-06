#!/usr/bin/env python
# -*- coding:utf-8 -*

'''
 Classe 
	Mère de toute les classes des composants
		qui se branchent sur notre priduino_io

 AUTEUR : FredThx

 Projet : rpiduino_io

'''
import time
from f_thread import *


class device_io (object):
	''' Classe decrivant un device a connecter à un	rpiduino_io
			(soit rpi_io ou pcduino_io)
	'''
	pass
		

class input_device_io(device_io):
	''' Composant de type capteur
			Ces composants peuvent générer un thread qui va scuter le capteur
			Et éventuellement générer une action
	'''
	def __init__(self, thread = False, on_changed = None, discard = None , pause = 0.1, timeout = 10):
		'''Initialisation du composant
				- thread		:	(facultatif) True si utilisation thread
				- on_changed	:	fonction ou string executable
									qui sera lancée quand la valeur du capteur change
				- discard		:	ecart en dessous duquel une valeur est considérée comme inchangée
				- pause 		:	pause entre chaque lecture du composant
				- timeout		:	durée après laquelle une valeur lue est obsolète
		'''
		self.on_changed = on_changed
		self.discard = discard
		self.pause = pause
		self.timeout = timeout
		self.last_read = None
		self.last_time_read = time.time()
		if thread:
			self.thread = f_thread(self.read_thread)
			self.thread.start()
		else :
			self.thread = False
	
	def add_thread(self, on_changed, discard = None , pause = 0.1, timeout = 10):
		'''Ajoute le mécanisme de thread a un composant qui n'en a pas
		'''
		assert (not self.thread), 'input_device_io has already a thread'
		input_device_io.__init__(self, True, on_changed, discard, pause, timeout)
	
	def read_thread(self):
		''' Lecture du capteur.
				Mise à jour last_read et last_time_read
				Exécution éventuelle du deamon on_changed
		'''
		value = self.read()
		self.last_time_read = time.time()
		if self.last_read == None:
			self.last_read = value
		elif self._value_changed(value):
			self.last_read = value
			self.changed()
		time.sleep(self.pause)
		return value
		
	def th_readed(self):
		''' Renvoie la dernière valeur lue si elle n'est pas obsolète
		'''
		if self.timeout == None or time.time()<self.last_time_read + self.timeout:
			return self.last_read
		else:
			return self.read_thread()
	
	def stop(self):
		'''Stop le thread du capteur
		'''
		if self.thread:
			self.thread.stop()
	
	def start(self):
		'''Redémarre le thread du capteur
		'''
		if self.thread and self.thread.terminated:
			self.thread.start()
	
	def changed(self):
		''' Execution de l'action on_changed
		'''
		if self.on_changed:
					if type(self.on_changed) is str:
						exec self.on_changed
					else:
						self.on_changed()

class digital_input_device_io(input_device_io):
	'''Capteur False/True
	'''
	def __init__(self, thread = False, on_changed = None, pause = 0.1, timeout = 10):
		'''Initialisation du composant
				- seuil 		:	seuil de detection en % (1=100%)
									soit un tuple (seuil_bas, seuil_haut)
									soit une seule valeur				
				- thread		:	(facultatif) True si utilisation thread
				- on_changed	:	fonction ou string executable
									qui sera lancée quand la valeur du capteur change
				- discard		:	ecart en dessous duquel une valeur est considérée comme inchangée
				- pause 		:	pause entre chaque lecture du composant
				- timeout		:	durée après laquelle une valeur lue est obsolète
		'''
		input_device_io.__init__(self, thread, on_changed, None, pause, timeout)
	
	def _value_changed(self, value):
		'''teste si la valeur est modifiee
		'''
		return (value != self.last_read)

class analog_input_device_io(input_device_io):
	''' Capteur analogique
	'''
	def __init__(self, seuil, thread = False, on_changed = None, discard = None , pause = 0.1, timeout = 10):
		'''Initialisation du composant
				- seuil 		:	seuil de detection en % (1=100%)
									soit un tuple (seuil_bas, seuil_haut)
									soit une seule valeur				
				- thread		:	(facultatif) True si utilisation thread
				- on_changed	:	fonction ou string executable
									qui sera lancée quand la valeur du capteur change
				- discard		:	ecart en dessous duquel une valeur est considérée comme inchangée
				- pause 		:	pause entre chaque lecture du composant
				- timeout		:	durée après laquelle une valeur lue est obsolète
		'''
		self.seuil = seuil	#Soit une valeur, soit un tuple
		if discard == None:
			discard = 0
		input_device_io.__init__(self, thread, on_changed, discard, pause, timeout)
	
	def _value_changed(self, value):
		'''teste si la valeur est modifiee
		'''
		return abs(value - self.last_read) > self.discard
		
	def high(self):
		""" Renvoie True si le capteur a une valeur au dessus du seuil
		"""
		if isinstance(self.seuil, tuple):
			seuil = self.seuil[1]
		else:
			seuil = self.seuil
		if self.thread:
			return self.th_readed() > seuil
		else:
			return self.read() > seuil
	
	def low(self):
		""" Renvoie True si le capteur a une valeur en dessous du seuil
		"""
		if isinstance(self.seuil, tuple):
			seuil = self.seuil[0]
		else:
			seuil = self.seuil
		if self.thread:
			return self.th_readed() < seuil
		else:
			return self.read() < seuil
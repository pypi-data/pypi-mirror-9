#!/usr/bin/env python
# -*- coding:utf-8 -*

"""
 Un capteur de mouvements
	SEN0018 de chez DF ROBOT
	
	Branchements/réglages
		- GRN	sur	0V
		- Vcc	sur 3.3V
		- sortie sur un GPIO
		
		jumper sur H
		potentiomètre à 0 (sinon, ça merde)
	
	Remarque : je ne suis pas sur que mon capteur fonctionne bien!
				et trace d'oxydation sur des soudures
	
 AUTEUR : FredThx

 Projet : rpiduino_io

"""
import time
from device_io import *
from pin_io import *
from f_thread import *


class sen0018_io (input_device_io):
	'''Capteur Infra Rouge detection de mouvement
	'''
	def __init__(self, pin, duration = 1, thread = False, on_detect = None, timeout = 30):
		'''Initialisation
			- pin		:	digital_pin_io
			- duration	:	temps de mesure
			- level		:	sensibilité (= durée de detection)
			- thread	:	Si True, lance un thread qui mesure en temps reel la detection
			- on_detect	:	fonction a executer en cas de detection
								soit sous forme de string
								soit sous forme de fonction
			- timeout	:	timeout pour remise à zéro dectection en cas de non lecture du capteur
		'''
		assert isinstance(pin, digital_pin_io), "pin doit être une digital_pin_io"
		self.pin = pin
		self.pin.setmode(INPUT)
		self.duration = duration
		self.last_detection = 0
		if thread:
			self.thread = f_thread(self.read_thread)
			self.thread.start()
		else :
			self.thread = False
		self.on_detect = on_detect
		self.timeout = timeout
	
	def read_raw(self):
		'''renvoie la lecture de la sortie du capteur
		'''
		return self.pin.get()
	
	def read(self):
		'''Renvoie True si le capteur detecte un mouvement pendant le temps de mesure
		'''
		if not self.thread:
			init_time = time.time()
			while time.time() < init_time + self.duration:
				time.sleep(1.*self.duration/50) #Libère un peu le processeur
				if self.read_raw():
					return True
			return False
		else:
			return (self.last_detection > time.time() - self.timeout)
	
	
	def read_thread(self):
		'''Lecture du capteur en tache de fond
		'''
		init_time = time.time()
		while time.time() < init_time + self.duration:
			if self.read_raw():
				self.last_detection = time.time()
				if self.on_detect:
					if type(self.on_detect) is str:
						exec self.on_detect
					else:
						self.on_detect()
			time.sleep(1.*self.duration/25)
	
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

#########################################################
#                                                       #
#		EXEMPLE                                         #
#                                                       #
#########################################################

if __name__ == '__main__':
	from led_io import *
	pc = rpiduino_io()		
	led = led_io(pc.pin[2])
	led.on()
	# sensor = sen0018_io(pc.pin[11], thread = False)
	# time.sleep(1)
	# while True:
		# if sensor.read():
			# led.on()
		# else:
			# led.off()
	def print_alerte():
		print 'Alerte %s' % time.strftime("%A %d %B %Y %H:%M:%S",time.timelocal(sensor.last_detection))
		time.sleep(5)
	
	sensor = sen0018_io(pc.pin[11], thread = True, on_detect = print_alerte, timeout=5)
	
	try:
		while True:
			if sensor.read():
				led.on()
			else:
				led.off()
			time.sleep(1)	#on a le temps
	except KeyboardInterrupt:
		sensor.stop()
	
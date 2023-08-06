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


class sen0018_io (digital_input_device_io):
	'''Capteur Infra Rouge detection de mouvement
	'''
	def __init__(self, pin, duration = 1, thread = False, on_changed = None, timeout = 30):
		'''Initialisation
			- pin		:	digital_pin_io
			- duration	:	temps de mesure
			- level		:	sensibilité (= durée de detection)
			- thread	:	Si True, lance un thread qui mesure en temps reel la detection
			- on_changed:	fonction a executer en cas de changement d'état
								soit sous forme de string
								soit sous forme de fonction
			- timeout	:	timeout pour remise à zéro dectection en cas de non lecture du capteur
		'''
		assert isinstance(pin, digital_pin_io), "pin doit être une digital_pin_io"
		self.pin = pin
		self.pin.setmode(INPUT)
		self.duration = duration
		digital_input_device_io.__init__(self, thread, on_changed, 1.*self.duration/25, timeout)
	
	def read(self):
		'''renvoie la lecture brute de la sortie du capteur
		'''
		return self.pin.get()
	
	def is_detect(self):
		'''Renvoie True si le capteur detecte un mouvement pendant le temps de mesure
		'''
		init_time = time.time()
		while time.time() < init_time + self.duration:
			time.sleep(1.*self.duration/25) #Libère un peu le processeur
			if self.read():
				return True
		return False
	
	



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
	# sensor = sen0018_io(pc.pin[11])
	# while True:
		# if sensor.read():
			# led.on()
		# else:
			# led.off()
	start = time.time()
	def print_alerte():
		if time.time()>start + 5:	# Pour laisser du temps au capteur de s'initialiser
			if sensor.th_readed():
				print 'Alerte %s ' % time.time()
				time.sleep(3)
	
	sensor = sen0018_io(pc.pin[11], thread = True, on_changed = print_alerte, timeout=5)
	try:
		while True:
			if sensor.is_detect():
				led.on()
			else:
				led.off()
			time.sleep(1)	#on a le temps
	except KeyboardInterrupt:
		sensor.stop()
	
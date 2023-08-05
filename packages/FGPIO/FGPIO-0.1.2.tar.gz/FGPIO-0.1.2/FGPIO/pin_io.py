#!/usr/bin/env python
# -*- coding:utf-8 -*

'''
	Description des pins sur rpiduino_io
'''


INPUT = 0
OUTPUT = 1
PULLUP = 8
SERIAL = 40
I2C = 42
SPI = 41
HIGH = 1
LOW = 0

import time
# On essaye importer le module RPi.GPIO
try:
	import RPi.GPIO
except: # Si nous sommes sur un pcduino, ça ne marchera pas
	pass
	
################################
#                              #
#    CLASSE de BASE : PIN_IO    #
#                              #
################################

class pin_io:
	"""  Port RPi ou PCDUINO
	"""
	def __init__(self, ):
		pass

class digital_pin_io(pin_io):
	""" Port numérique RPi ou Pcduino
	"""
	def __init__(self, ):
		pass
	
	def invert(self):
		"""Inverse l'état d'un port
		"""
		if self.getmode()==OUTPUT:
			if self.get() == HIGH:
				self.set(LOW)
			else:
				self.set(HIGH)
		else:
			raise rpiduino_io_error('Impossible de realiser invert(). Le port' + self.physical_id + ' n''est pas OUTPUT')
	
	def pulseOut(self, duree):
		if self.getmode()==OUTPUT:
			self.invert()
			time.sleep(duree)
			self.invert()
		else:
			raise rpiduino_io_error('Impossible de realiser pulseOut. Le port n est pas OUTPUT')
		
	#TODO PWM
	
################################
#                              #
#    DUINO_IO                  #
#                              #
################################

class duino_pin_io(pin_io):
	""" Port IO d'un pcduino
	"""
	def __init__(self, id, base_path):
		""" id = n° du port
				0,1,2,...,13 pour les port numériques
				A0,A1,..., A5 pour les ports analogiques
		"""
		self.logical_id = id
		self.physical_id = id
		self.base_path = base_path

class digital_puino_pin_io(duino_pin_io,digital_pin_io):
	""" Port digital d'un pcduino
	"""
	def __init__(self, id):
		""" id = n° du port
				0,1,2,...,13 pour les ports numériques
		"""
		duino_pin_io.__init__(self, id, '/sys/devices/virtual/misc/gpio/')
	
	def setmode(self, mode):
		""" Definit le mode de la pin numériques
				INPUT = 1 
				OUTPUT = 0
		"""
		file=open(self.base_path+"mode/gpio"+str(self.logical_id),'w') # ouvre le fichier en ecriture
		file.write(str(mode)) # ecrit dans le fichier le mode voulu
		file.close()
	
	def getmode(self):
		""" Extrait le mode du la pin
		"""
		file=open(self.base_path+"mode/gpio"+str(self.logical_id),'r')
		file.seek(0)
		mode=file.read()
		file.close()
		return int(str(mode)[0])
		
	def get(self):
		""" Renvoie la valeur de la pin numérique
		"""
		file=open(self.base_path+"pin/gpio"+str(self.logical_id),'r') # ouvre le fichier en lecture
		file.seek(0) # se place au debut du fichier
		valeur=file.read()  #lit le fichier
		file.close()
		return int(valeur)
	
	def set(self, value):
		""" Assigne la valeur à la pin
			HIGH = 1
			LOW = 0
		"""
		global OUTPUT, HIGH, LOW
		if self.getmode() == OUTPUT:
			if value in (HIGH, LOW):
				value = str(value)		
				file=open(self.base_path+"pin/gpio"+str(self.logical_id),'w') # ouvre le fichier en ecriture
				file.write(value)
				file.close()
			else:
				raise rpiduino_io_error('Impossible assigner la valeur ' + value + " à la pin " + self.__repr__())
		else:
			raise rpiduino_io_error('La pin " + self.__repr__() + " est en lecture seule.')

	def __repr__(self):
		if self.getmode() == OUTPUT:
			mode = "OUTPUT"
		else:
			mode = "INPUT"
		return str(self.logical_id) + " : E/S Digitale en mode " + mode + ". Valeur = " + str(self.get())

class analog_puino_pin_io(duino_pin_io):
	""" Port analogique d'un pcduino
	"""
	def __init__(self, id):
		""" id = n° du port de 0 à 5
		"""
		if str(id)[0]=='A':
			duino_pin_io.__init__(self, id, '/proc/')
		else:
			duino_pin_io.__init__(self, 'A' + str(id), '/proc/')
	
	def get(self):
		""" renvoie la valeur de la pin analogique
		"""
		file=open(self.base_path+'adc'+str(self.logical_id[1]),'r')
		file.seek(0)
		valeur=file.read()
		file.close()
		valeur=valeur.split(":")[1] # On extrait ce qui est après le ":"
		return int(valeur)
		
	def get_voltage(self):
		""" Renvoie le voltage sur la pin
				63 = 2 Volts
		"""
		return self.max_voltage * self.get() / self.max_value
	
class small_analog_puino_pin_io(analog_puino_pin_io):
	""" Port A0 ou A1 (broches en 6 bits sur une plage de 0-2V)
	"""
	def __init__(self, id):
		"""
		"""
		analog_puino_pin_io.__init__(self,id)
		self.max_voltage = 2.
		self.max_value = 63
	
	def __repr__(self):
		return str(self.logical_id) + " : E/S Analogique 6bits. Valeur = " +str( self.get()) + " soit " + str(self.get_voltage()) + "V"

class high_analog_puino_pin_io(analog_puino_pin_io):
	""" Port A2 à A5 (broches en 12 bits sur une plage de 0-3.3V)
	"""
	def __init__(self, id):
		"""
		"""
		analog_puino_pin_io.__init__(self,id)
		self.max_voltage = 3.3
		self.max_value = 4095
	
	def __repr__(self):
		return str(self.logical_id) + " : E/S Analogique 12bits. Valeur = " + str(self.get()) + " soit " + str(self.get_voltage()) + "V"

################################
#                              #
#    RPI_IO                    #
#                              #
################################


class digital_rpi_pin_io(digital_pin_io):
	""" Port IO d'un RPI
	"""
	def __init__(self, physical_id, logical_id, bmc_id):
		"""Initilalisation d'un port GPIO_RPI
		"""
		self.physical_id = physical_id
		self.logical_id = logical_id
		self.bmc_id = bmc_id
		
	def setmode(self, mode):
		""" Definit le mode de la pin 
				INPUT = 1 
				OUTPUT = 0
		"""
		# A NOTER QUE (juste pour nous aider!!!)
		# RPi.GPIO.OUT = 0		INPUT = 1
		# RPi.GPIO.IN = 1		OUTPUT = 0
		if mode == INPUT:
			RPi.GPIO.setup(self.physical_id, RPi.GPIO.IN)
		if mode == PULLUP:
			RPi.GPIO.setup(self.physical_id, RPi.GPIO.IN, RPi.GPIO.PUD_UP)
		elif mode == OUTPUT:
			RPi.GPIO.setup(self.physical_id, RPi.GPIO.OUT)
		elif mode == SERIAL:
			RPi.GPIO.setup(self.physical_id, RPi.GPIO.SERIAL)
		elif mode == I2C:
			RPi.GPIO.setup(self.physical_id, RPi.GPIO.I2C)
		elif mode == SPI:
			RPi.GPIO.setup(self.physical_id, RPi.GPIO.SPI)
			
	def getmode(self):
		""" Extrait le mode du la pin
		"""
		mode = RPi.GPIO.gpio_function(self.physical_id)
		if mode == RPi.GPIO.OUT:
			return OUTPUT
		elif mode == RPi.GPIO.IN:
			return INPUT
		elif mode == RPi.GPIO.SERIAL:
			return SERIAL
		elif mode == RPi.GPIO.I2C:
			return I2C
		elif mode == RPi.GPIO.SPI:
			return SPI
		else:
			return None
			
	def get(self):
		""" Renvoie la valeur de la pin numérique
		"""
		try:
			valeur = RPi.GPIO.input(self.physical_id)
		except:# Si le mode du port n'est pas définit, on renvoie 0
			valeur = 0
		return valeur
	
	def set(self, value):
		""" Assigne la valeur à la pin
		"""
		if self.getmode() != INPUT:
			RPi.GPIO.output(self.physical_id, int(value))
		else:
			raise rpiduino_io_error('La pin ' + self.__repr__() + ' est en lecture seule.')
	
	def __repr__(self):
		mode = self.getmode()
		if mode == OUTPUT:
			mode = "OUTPUT"
		elif mode == INPUT:
			mode = "INPUT"
		elif mode == SERIAL:
			mode = "SERIAL"
		elif mode == I2C:
			mode = "I2C"
		elif mode == SPI:
			mode = "SPI"
		return str(self.physical_id) + " : GPIO en mode " + mode + ". Valeur = " + str(self.get())	
	
	
	
################################
#                              #
#    GESTION DES ERREURS       #
#                              #
################################
		
class rpiduino_io_error(Exception):
	def __init__(self, message):
		self.message = message
	def __str__(self):
		return self.message
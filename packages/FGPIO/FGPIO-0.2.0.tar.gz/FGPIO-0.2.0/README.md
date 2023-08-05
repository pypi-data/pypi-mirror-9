FGPIO Lib - Une librairie pour gerer les e/s d'un RPi ou d'un pcduino
========================================================================

Ce module permet de gerer les composants suivants avec un Raspberry PI ou un pcduino

	-	Rpi ou pcduino	avec 	rpiduino_io
	-	Bouton			avec 	bt_io
	-	Led				avec	led_io
	-	lcd				avec 	lcd_io
	-	luminosite		avec	lum_capteur_io
	-	max7219			avec	max7219_io
	-	des prises radios commandees
						avec	rcSwitch_io et prises
	-	Capteur de distance UltraSon
						avec	UltraSonic_io
	-	Extention de GPIO
					MCP23017
						avec 	mcp23017_io
					PCA9555 (DF ROBOT DFR0013)
						avec	pca9555_io
	-	bouton rotatif
						avec 	rotary_encoder_io
	-	gestion d'un menu
						avec 	f_menu

Installation :
	pip install FGPIO

Exemple d'usage :
	
>>>from FGPIO.rpiduino_io import *
>>>from FGPIO.led_io import *
>>>pc = rpiduino_io()
>>>led = led_io(pc.logical_pin(2))
>>>led.on()
	
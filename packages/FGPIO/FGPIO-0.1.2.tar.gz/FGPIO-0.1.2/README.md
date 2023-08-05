FGPIO Lib - Une librairie pour gerer les e/s d'un RPi ou d'un pcduino
========================================================================

Ce module permet de gerer les composants suivants avec un Raspberry PI ou un pcduino

	-	Bouton		avec 	bt_io
	-	Led			avec	led_io
	-	lcd			avec 	lcd_io
	-	luminosite	avec	lum_capteur_io
	-	max7219		avec	max7219_io
	-	des prises radios commandees
					avec	rcSwitch_io et prises
	-	Capteur de distance UltraSon
					avec	UltraSonic_io

	Installation :
		pip install FGPIO
	
	Exemple d'usage :
	
	>>>from FGPIO.rpiduino_io import *
	>>>from FGPIO.led_io import *
	>>>pc = rpiduino_io()
	>>>led = led_io(pc.logical_pin(2))
	>>>led.on()
	
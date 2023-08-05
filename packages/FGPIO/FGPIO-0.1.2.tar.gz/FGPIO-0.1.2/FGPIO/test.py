#!/usr/bin/env python
# -*- coding:utf-8 -*

from rpiduino_io import *
from lum_capteur_io import *
from lcd_i2c_io import *
from led_io import *
from bt_io import *
import time

pc=rpiduino_io()

lcd = lcd_i2c_io(2,0x20)
luminosite = lum_capteur_io(pc.pin['A5'],.99)
led = led_io(pc.pin[2])
bt = bt_io(pc.pin[3])


while True:
	lcd.message("Lum : " + str(int(100*luminosite.read())) + '%',1)
	if bt.is_pressed:
		lcd.message('LOL',2)
		led.on()
	else:
		lcd.message('merci d appuyer sur le bouton',2,True)
		led.off()
	#time.sleep(0.5)
	
	



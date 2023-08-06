#!/usr/bin/env python
# -*- coding:utf-8 -*

import threading
import sys
import time
"""
	Une petite classe de Thread
		basée sur threading
		ou l'on passe une fonction en arguments
		
		usage : mon_thread = f_thread(ma_fonction, arg1, arg2, ..., nom_arg = arg, ...)
				mon_thread.start()
"""

class f_thread(threading.Thread):
	def __init__(self, fonction, *args, **kwargs):
		"""Initialisation
				- fonction		:	une fonction
				- args, kwargs	:	ses arguments
		"""
		threading.Thread.__init__(self)
		self.fonction = fonction
		self.args = args
		self.kwargs = kwargs
		self.terminated = False
		
	def run(self):
		print self.fonction.__name__ + ' started.'
		loops = 0
		while not self.terminated:
			#try:
			self.fonction(*self.args, **self.kwargs)
			loops += 1
		print self.fonction.__name__ + ' stopped after %s loops' % loops
			#except Exception:
			#	print "Unexpected error:", sys.exc_info()[0], 'in', self.fonction
	def stop(self):
		self.terminated = True

#########################################################
#                                                       #
#		EXEMPLE                                         #
#                                                       #
#########################################################


if __name__ == '__main__':
	import time
	def f1(a):
		print a
	def f2():
		print 'f2'
	def f3():
		print 'f3'
		
	th_f1 = f_thread(f1,"f1")
	th_f2 = f_thread(f2)
	th_f3 = f_thread(f3)

	th_f1.start()
	th_f2.start()
	th_f3.start()

	# Pour pouvoir planter le programme en ctrl-c
	try:
		while True:
			time.sleep(2)
	except KeyboardInterrupt:
		th_f1.stop()
		th_f2.stop()
		th_f3.stop()
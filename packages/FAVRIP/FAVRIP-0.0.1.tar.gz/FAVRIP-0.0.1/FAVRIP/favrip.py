#!/usr/bin/env python
# -*- coding:utf-8 -*

'''
Class favrip

	Pour communication avec Audio Video Receiver IP
	

'''
import socket
import functools
import time

class favrip(object):
	''' A Audio Video Receiver with ethernet link
	'''
	def __init__(self, adr_ip, timeout = 2, port = 23):
		'''Initialisation
			- adr_ip	:	ip adress
			- timeout
			- port
		'''
		self.adr_ip = adr_ip
		self.timeout = timeout
		self.port = port
		self.update()
	
	def update(self):
		'''Mise a jour de la connection a l'ampli'''
		try:
			self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self.sock.connect((self.adr_ip, self.port))
			self.sock.settimeout(self.timeout)
		except (EOFError, socket.error, ValueError, socket.timeout), err:
			print err
	
	def unError(fonction):
		'''Decorateur pour eviter les erreurs
		Si erreur dans une des methodes, on essaye de reconnecter le serveur 1 fois
		Si ca ne passe toujours pas, on abandonne'''
		@functools.wraps(fonction) # ca sert pour avoir un help(SBClient) utile
		def SBUnErrorFonction(self,*args, **kwargs):
			try:
				return fonction(self,*args, **kwargs)
			except :
				self.update()
				try:
					return fonction(self,*args, **kwargs)
				except:
					return None
		return SBUnErrorFonction
	
	@staticmethod
	def trys(fonction):
		'''Décorateur pour tester 4 fois la fonction
		'''
		@functools.wraps(fonction) # ca sert pour avoir un help(SBClient) utile
		def SBUnErrorFonction(self, trys = 4):
			if trys < 1:
				return None
			else:
				try:
					return fonction(self)
				except:
					SBUnErrorFonction(self, trys - 1)
		return SBUnErrorFonction
	
	@unError	
	def command(self, cmd):
		'''Execute l'action cmd
		'''
		self.sock.send(cmd + '\r')
		time.sleep(0.25) # Pour être sur de bien lire le retour
		data = self.sock.recv(1024)
		return data
	
	def execute(self, command, arg, value = None):
		''' Execute a command
			- command	ex : MasterVolume
			- arg		ex : set
			- value		ex : 30
		'''
		try:
			if value == None:
				return self.command(self.COMMANDS[command][arg])
			else:
				return self.command(self.COMMANDS[command][arg] % value)
		except KeyError:
			return 'KeyError'
	
	def on(self):
		''' Turn on the AVR'''
		self.execute('Power', 'on')
	
	def standby(self):
		''' Turn off the AVR'''
		self.execute('Power', 'off')
	
	def off(self):
		''' Turn off the AVR'''
		self.execute('Power', 'off')
	
	def set_power(self, arg='on'):
		''' Turn the power on(defaut)/off '''
		self.execute('Power', arg)
	
	def volume_up(self):
		''' Set the volume up'''
		self.execute('MasterVolume','up')
	
	def volume_down(self):
		''' Set the volume down'''
		self.execute('MasterVolume','down')
	
	def set_volume(self, volume):
		''' Set the volume'''
		self.execute('MasterVolume', 'set', volume)
	
	def set_input(self, source):
		''' Set the input source'''
		self.execute('Input', source)

	def set_input_and_play(self, source):
		''' Set the input source and play it'''
		self.execute('InputAndPlay', source)
	
	def set_aux2(self):
		'''set the input source to aux2'''
		self.execute('Input','aux2')
		
	def set_main_zone(self, arg='on'):
		''' Set the main zone on(defaut)/off'''
		self.execute('MainZone', arg)
	
	def set_sleep_timer(self, arg = 'on', value = 60):
		''' Set the sleep timer on(defaut)/off
			- value		:	delay in secondes (default = 60)
		'''
		if arg == 'off':
			value = None
		self.execute('SleepTimer', arg, value)


	
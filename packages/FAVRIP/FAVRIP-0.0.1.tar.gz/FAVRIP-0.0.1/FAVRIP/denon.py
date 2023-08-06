#!/usr/bin/env python
# -*- coding:utf-8 -*

'''
Class denonARV

	Pour communication avec ARV Denon
	
	Models :
	Models :
		- AVR-3311CI
		- AVR-3311
		- AVR-991
		- AVR-X2100W (tested)
		- ...

'''
import socket
import functools
import time
from favrip import *

class denonARV(favrip):
	'''Un ampli Video DENON
	'''
	COMMANDS = {
		'Power': {
		'on': 'PWON',
		'off': 'PWSTANDBY',
		'get' : 'PW?'
		},
		'MasterVolume': {
		'up': 'MVUP',
		'down': 'MVDOWN',
		'set': 'MV%02i',
		'get': 'MV?'
		},
		'Mute': {
		'on': 'MUON',
		'off': 'MUOFF'
		},
		'Input': {
		'phono': 'SIPHONO',
		'cd': 'SICD',
		'tuner': 'SITUNER',
		'dvd': 'SIDVD',
		'bluray': 'SIBD',
		'tv': 'SITV',
		'cable': 'SISAT/CBL',
		'dvr': 'SIDVR',
		'game': 'SIGAME',
		'game2': 'SIGAME2',
		'v.aux': 'SIV.AUX',
		'aux1': 'SIAUX1',
		'aux2': 'SIAUX2',
		'mplay': 'SIMPLAY',
		'usb': 'SIUSB/IPOD',
		'ipod': 'SIIPOD DIRECT',
		'dock': 'SIDOCK',
		'net_usb': 'SINET/USB',
		'lastfm': 'SILASTFM',
		'net': 'SINET',
		'bt': 'SIBT',
		'flickr': 'SIFLICKR',
		'favorites': 'SIFAVORITES',
		'iradio': 'SIIRADIO',
		'server': 'SISERVER',
		'get': 'SI?'
		},
		'InputAndPlay': {
		'ipod': 'SIIPOD',
		'usb': 'SIUSB',
		'ipod_direct': 'SIIPD',
		'iradio': 'SIIRP',
		'favorites': 'SIFVR'
		},
		'MainZone': {
		'on': 'ZMON',
		'off': 'ZMOFF',
		'get': 'ZM?'
		},
		'SleepTimer': {
		'off': 'SLPOFF',
		'on': 'SL%02i'
		}
		}
	
	@favrip.trys
	def get_power(self):
		''' Return 'on' ou 'off' '''
		reponse =  self.execute('Power', 'get')
		if reponse[0:4] == 'PWON':
			return 'on'
		elif reponse[0:9] == 'PWSTANDBY':
			return 'off'
		else:
			raise socket.error
	
	@favrip.trys
	def get_volume(self):
		'''Get the  Volume'''
		reponse = self.execute('MasterVolume', 'get')
		return int(reponse[2:4])
	
	@favrip.trys
	def get_input(self):
		''' Get the input source'''
		reponse = self.execute('Input', 'get')
		if reponse[0:2]!='SI':
			raise socket.error
		return reponse.split('\r')[0][2:]

#########################################################
#                                                       #
#		EXEMPLE                                         #
#                                                       #
#########################################################

if __name__ == '__main__':
	ampli = denonARV('192.168.10.175')
	ampli.on()
	ampli.set_aux2()
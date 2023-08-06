FAVRIP Lib - Une librairie pour piloter un Amplie Audio Video
========================================================================

Ce module permet de piloter via TCP_IP un ammpli Home cinema

	- DENON 
	- autres : a configurer
	
	
Installation :
	pip install FAVRIP

Exemple d'usage :
	
>>>from FAVRIP.denon import *
>>>ampli = denonAVR('192.168.0.30')
>>>ampli.on()
>>>ampli.set_input('tv')
	
#!/usr/bin/env python

import socket, getopt, sys

# default unit
unit = "MAIN"

# default hostname and port
hostname = "av"
port = "50000"

class YamahaException(Exception):
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return self.value

class Yamaha:
	def __init__(self, hostname, port):
		self.zone = "MAIN"
		self.hostname = hostname
		self.port = port

	def send(self, zone, command, arguments):
		command = "@%s:%s=%s\r\n" % (zone, command, arguments)
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.settimeout(1.0)
		try:
			s.connect(("av", 50000))
			s.send(command)
			data = s.recv(512)
			s.close()
			if "@UNDEFINED" in data or "@RESTRICTED" in data:
				raise YamahaException("message: %s response: %s" % (command, data))
			data = dict([line[1:].split("=") for line in data.split("\r\n") if len(line) != 0])
			return data
		except socket.timeout as command:
			raise YamahaException("No connection.")
	
	def get(self, command, *args, **kwargs):
		zone = kwargs["zone"] if "zone" in kwargs else self.zone
		data = self.send(zone, command, "?")
		return data["%s:%s" % (zone, command)]
	
	def put(self, command, argument, *args, **kwargs):
		zone = kwargs["zone"] if "zone" in kwargs else self.zone
		return self.send(zone, command, argument)

	def getVolume(self):
		return float(self.get("VOL"))
	def setVolume(self, volume):
		self.put("VOL", volume)

	def getPower(self):
		return self.get("PWR", zone="MAIN") == "On"
	def setPower(self, power):
		self.put("PWR", "On" if power else "Standby")
	def togglePower(self):
		self.put("PWR", "On/Off")

	def getMute(self):
		return self.get("MUTE") == "On"
	def setMute(self, mute):
		self.put("MUTE", "On" if mute else "Off")
	def toggleMute(self):
		self.put("MUTE", "On/Off")

	def getInput(self):
		return self.get("INP")
	def setInput(self, input):
		self.put("INP", input)

	def getSoundProgram(self):
		return self.get("SOUNDPRG")
	def setSoundProgram(self, program):
		self.put("SOUNDPRG", program)

usage = "Usage: " + sys.argv[0] + """ [-h] [-a HOSTNAME] [-p PORT] [-u UNIT] -c COMMAND [PARAMETERS]
Sends YNCA commands to Yamaha AV receivers.  Tested with an RX-V675, but should work with many others.

Class includes member functions for common operations to ease integration with other scripts.

Common examples:
VOL Up
VOL -12.5
VOL Up 5 dB
MUTE On
MUTE Off
MUTE On/Off          (toggle)
INP HDMI1
SOUNDPRG 2ch Stereo
PWR On
PWR Standby
PWR On/Standby

Full documentation at http://thinkflood.com/media/manuals/yamaha/Yamaha-YNCA-Receivers.pdf
"""

if __name__ == "__main__":
	try:
		opts, args = getopt.getopt(sys.argv[1:], "ha:p:u:", ["address=", "port=", "unit="])
	except:
		print usage
		sys.exit(1)
	if len(args) == 0:
		print usage
		sys.exit(1)
	command = args[0].upper()
	arguments = ' '.join(args[1:])
	for opt, arg in opts:
		if opt in ("-h"):
			print usage
			sys.exit(0)
		if opt in ("-a", "--address"):
			hostname = arg
		if opt in ("-p", "--port"):
			port = int(arg)
		if opt in ("-u", "--unit"):
			unit = arg.upper()

	y = Yamaha(hostname, port)
	print y.send(unit, command, arguments)


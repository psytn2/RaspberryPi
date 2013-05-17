#!/usr/bin/python
#thanks to adafruit.com forum that helped me to understand how Raspberry PI works
#Luxmeter class taken from user Huelke of adafruit.com forum

#The code has been tested on a Raspberry Pi 512mb v2
#The luminosity sensor is the Adafruit tsl2561 and a normal led connected at the port 17 of the GPIO

import RPi.GPIO as GPIO
import sys
import smbus
import time
from Adafruit_I2C import Adafruit_I2C

class Luxmeter:
	i2c = None
	def __init__(self, address=0x39, debug=0, pause=0.8):
		self.i2c = Adafruit_I2C(address)
		self.address = address
		self.pause = pause
		self.debug = debug
		self.gain = 0 # No gain preselected
		self.i2c.write8(0x80, 0x03) # Enable device

	def setGain(self, gain=1):
		""" Set the gain """
		if(gain != self.gain):
			if (gain == 1):
				self.i2c.write8(0x81, 0x02) # set gain = 1X and timing = 402 mSec
			if (self.debug):
				print "Setting low gain"
			else:
				self.i2c.write8(0x81, 0x12) # set gain = 16X and timing = 402 mSec
				if(self.debug):
					print "Setting high gain"
			self.gain = gain; # Safe gain for calculation
			time.sleep(self.pause) # pause for integration (self.pause must be higger than integration time)

	
	def readWord(self, reg):
		"""Reads a word from the I2C device"""
		try:
			wordval = self.i2c.readU16(reg)
			newval = self.i2c.reverseByteOrder(wordval)
			if(self.debug):
				print("I2C: Device 0x%02X returned 0x%04X from reg 0x%02X" % (self.address, wordval & 0xFFFF, reg))
			return newval
		except IOError:
			print("Error accessing 0x%02X: Check your I2C address" % self.address)
			return -1
	

	def readFull(self, reg=0x8C):
		"""Reads visible+IR diode from the I2C device"""
		return self.readWord(reg);

	def readIR(self, reg=0x8E):
		"""Reads IR only diode from the I2C device"""
		return self.readWord(reg);

	def getLux(self, gain = 0):
		"""Grabs a lux reading either with autoranging (gain = 0) or with a specified gain (1, 16)"""
		if(gain == 1 or gain == 16):
			self.setGain(gain) #low/highGain
			ambient = self.readFull()
			IR = self.readIR()
		elif (gain==0): # auto gain
			self.setGain(16) #first try highGain
			ambient = self.readFull()
			if (ambient < 65535):
				IR = self.readIR()
			if (ambient >= 65535): #value(s) exceed(s) datarange
				self.setGain(1) # set lowGain	
				ambient = self.readFull()
				IR = self.readIR()
		
		if(self.gain==1):
			ambient *= 16 # scale 1x to 16x
			IR *= 16 # scale 1x to 16x
	
		ratio = (IR / float(ambient)) # changed to make it run under python 2
	
		if (self.debug):
			print "IR Result", IR
			print "Ambient Result", ambient

		if((ratio >= 0) & (ratio <= 0.52)):
			lux = (0.0315 * ambient) - (0.0593 * ambient * (ratio **1.4))
		elif (ratio <= 0.65):
			lux = (0.0229 * ambient) - (0.0291 * IR)
		elif (ratio <= 0.80):
			lux = (0.0157 * ambient) - (0.018 * IR)
		elif (ratio <= 1.3):
			lux = (0.00338 * ambient) - (0.0026 * IR)
		elif (ratio > 1.3):
			lux = 0

		return lux

class Led:
	global pinNum
	pinNum = 17

	def __init__(self):
		GPIO.setmode(GPIO.BCM)
		GPIO.setup(pinNum, GPIO.OUT)

	def isLuxLow(self, lux):
		if(lux>7000):
			for x in range(0,3):
				GPIO.output(pinNum, GPIO.HIGH)
				time.sleep(0.5)
				GPIO.output(pinNum, GPIO.LOW)
				time.sleep(0.5)
		

def main():
			
	oLuxmeter = Luxmeter()
	oLed = Led()

	print "LUX HIGH GAIN", oLuxmeter.getLux(16)
	print "LUX LOW GAIN", oLuxmeter.getLux(1)
	print "LUX AUTO GAIN", oLuxmeter.getLux()

	oLed.isLuxLow(oLuxmeter.getLux(1))
	GPIO.cleanup()

__name__ == '__main__' and main()

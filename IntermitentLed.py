#intermitent led for 5 seconds

import RPi.GPIO as GPIO
import sys
import smbus
import time

class Led:
	global pinNum
	pinNum = 17

	def __init__(self):
		GPIO.setmode(GPIO.BCM)
		GPIO.setup(pinNum, GPIO.OUT)

	def start(self):
		for x in range(0, 5):	
			GPIO.output(pinNum, GPIO.HIGH)
			time.sleep(0.5)
			GPIO.output(pinNum, GPIO.LOW)
			time.sleep(0.5)
		

def main():

	oLed = Led()
	oLed.start()
	GPIO.cleanup()

__name__ == '__main__' and main()

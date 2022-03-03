import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setup(4,GPIO.OUT)



while True:
	inputIO = GPIO.input(5)
	print(inputIO)



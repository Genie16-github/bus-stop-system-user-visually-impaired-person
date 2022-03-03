import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setup(17,GPIO.IN,pull_up_down=GPIO.PUD_UP)
GPIO.setup(27,GPIO.IN,pull_up_down=GPIO.PUD_UP)
GPIO.setup(22,GPIO.IN,pull_up_down=GPIO.PUD_UP)

while True:
    print("17 : ",GPIO.input(17))
    print("22 : ",GPIO.input(22))
    print("27 : ",GPIO.input(27))
    time.sleep(1)
    


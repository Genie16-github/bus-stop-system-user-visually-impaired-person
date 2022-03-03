import RPi.GPIO as GPIO
import time
import re
import time
import argparse
from threading import Thread
from luma.led_matrix.device import max7219
from luma.core.interface.serial import spi, noop
from luma.core.render import canvas
from luma.core.virtual import viewport
from luma.core.legacy import text, show_message
from luma.core.legacy.font import proportional, CP437_FONT, TINY_FONT, SINCLAIR_FONT, LCD_FONT
GPIO.setmode(GPIO.BCM)
GPIO.setup(17,GPIO.IN,pull_up_down=GPIO.PUD_UP)
GPIO.setup(22,GPIO.IN,pull_up_down=GPIO.PUD_UP)
GPIO.setup(27,GPIO.IN,pull_up_down=GPIO.PUD_UP)

signal=0
signal1=0
temp1=0
temp2=0
def but_fun(device,device1,th1,th2):
	global signal
	global signal1

	while True:
		while True:
			if GPIO.input(17) == False and signal==0:
				signal = 1
				th1.start()
				break
			elif GPIO.input(27) == False and signal1==0:
				signal1 = 1
				th2.start()
				break
		

def fun1(device):
    while True:
        with canvas(device) as draw:
            text(draw, (5, 0), "151", fill="white")
            time.sleep(0.1)
        
def fun2(device):
    while True:
        with canvas(device) as draw:
            text(draw, (5, 0), "402", fill="white")
            time.sleep(0.1)
            
    
def demo(n, block_orientation, rotate, inreverse):
    # create matrix device
    serial = spi(port=0, device=0, gpio=noop())
    device = max7219(serial, cascaded=n or 1, block_orientation=block_orientation,
                     rotate=rotate or 0, blocks_arranged_in_reverse_order=inreverse)
    serial1 = spi(port=0, device=1, gpio=noop())
    device1 = max7219(serial1, cascaded=n or 1, block_orientation=block_orientation,
                     rotate=rotate or 0, blocks_arranged_in_reverse_order=inreverse)
    
    th1 = Thread(target=fun1,args=(device1,))
    th2 = Thread(target=fun2,args=(device,))

    but_fun(device,device1,th1,th2)



    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='matrix_demo arguments',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('--cascaded', '-n', type=int, default=4, help='Number of cascaded MAX7219 LED matrices')
    parser.add_argument('--block-orientation', type=int, default=90, choices=[0, 90, -90], help='Corrects block orientation when wired vertically')
    parser.add_argument('--rotate', type=int, default=0, choices=[0, 1, 2, 3], help='Rotate display 0=0°, 1=90°, 2=180°, 3=270°')
    parser.add_argument('--reverse-order', type=bool, default=True, help='Set to true if blocks are in reverse order')

    args = parser.parse_args()

    try:
        demo(args.cascaded, args.block_orientation, args.rotate, args.reverse_order)
    except KeyboardInterrupt:
        pass

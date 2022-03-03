import RPi.GPIO as GPIO
import time
import re
import cv2
import requests
import sys
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

LIMIT_PX = 1024
LIMIT_BYTE = 1024*1024  # 1MB
LIMIT_BOX = 40
signal=0
signal1=0
temp1=0
temp2=0

def kakao_ocr_resize(image_path: str):
    """
    ocr detect/recognize api helper
    ocr api의 제약사항이 넘어서는 이미지는 요청 이전에 전처리가 필요.

    pixel 제약사항 초과: resize
    용량 제약사항 초과  : 다른 포맷으로 압축, 이미지 분할 등의 처리 필요. (예제에서 제공하지 않음)

    :param image_path: 이미지파일 경로
    :return:
    """
    image = cv2.imread(image_path)
    height, width, _ = image.shape

    if LIMIT_PX < height or LIMIT_PX < width:
        ratio = float(LIMIT_PX) / max(height, width)
        image = cv2.resize(image, None, fx=ratio, fy=ratio)
        height, width, _ = height, width, _ = image.shape

        # api 사용전에 이미지가 resize된 경우, recognize시 resize된 결과를 사용해야함.
        image_path = "{}_resized.jpg".format(image_path)
        cv2.imwrite(image_path, image)

        return image_path
    return None


def kakao_ocr(image_path: str, appkey: str):
    """
    OCR api request example
    :param image_path: 이미지파일 경로
    :param appkey: 카카오 앱 REST API 키
    """
    API_URL = 'https://dapi.kakao.com/v2/vision/text/ocr'

    headers = {'Authorization': 'KakaoAK {}'.format(appkey)}

    image = cv2.imread(image_path)
    jpeg_image = cv2.imencode(".jpg", image)[1]
    data = jpeg_image.tobytes()


    return requests.post(API_URL, headers=headers, files={"image": data})

def receiveImg(img,appkey):
    output = kakao_ocr(img, appkey).json()
    i = 0
    words=""
    while True:
        try:
            words= words + str(output['result'][i]['recognition_words'])[2:]
            words = words[:-2]
            i = i+1
        except:
            break
    return words

def carnumber_detect():
    if len(sys.argv) != 3:
        print("Please run with args: $ python example.py /path/to/image appkey")
    image_path, appkey = 'bus_test2.jpg','0d0dbe871dc8ec1ca2a95a5dac00572f'


    resize_impath = kakao_ocr_resize(image_path)
    if resize_impath is not None:
        image_path = resize_impath
        print("원본 대신 리사이즈된 이미지를 사용합니다.")

    output = kakao_ocr(image_path, appkey).json()
    #print("[OCR] output:\n{}\n".format(json.dumps(output, sort_keys=True, indent=2, ensure_ascii=False)))  # 변경 후
    i = 0
    words=""
    while True:
        try:
            words= words + str(output['result'][i]['recognition_words'])[2:]
            words = words[:-2]
            i = i+1
        except:
            break
    print(words)
    return words

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
            
def fun3(device):
    while True:
        with canvas(device) as draw:
            text(draw, (1, 0), "2016", fill="white")
            time.sleep(0.1)

def demo(n, block_orientation, rotate, inreverse):
    # create matrix device
    serial = spi(port=0, device=0, gpio=noop())
    device = max7219(serial, cascaded=n or 1, block_orientation=block_orientation,
                     rotate=rotate or 0, blocks_arranged_in_reverse_order=inreverse)
    serial1 = spi(port=0, device=1, gpio=noop())
    device1 = max7219(serial1, cascaded=n or 1, block_orientation=block_orientation,
                     rotate=rotate or 0, blocks_arranged_in_reverse_order=inreverse)
    
    th1 = Thread(target=fun1,args=(device,))
    th2 = Thread(target=fun2,args=(device1,))

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


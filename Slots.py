#from selenium import webdriver

#from pyvirtualdisplay import Display
import pyautogui
import time
import pyscreenshot as ImageGrab
import matplotlib.pyplot as plt
from sklearn.svm import SVC
from sklearn.svm import LinearSVC
#import cv2

from scipy import misc
#from utils import *
from Q_learning import *
from draw_step import *

left = 56
up = 88

grab_images = False
learn_classifier = True
online = True


def grab_rect(clf):
	im=ImageGrab.grab(bbox=(442 + left,490 + up,552 + left,540 + up))
	img = im.convert('L')
	img = np.asarray(img)
	card = clf.predict(img.flatten().reshape(1, -1))[0]
	return card

def move(action):
	if action == 0:
		pyautogui.moveTo(642 + left, 267 + up)
		pyautogui.click()

	if action == 1:
		pyautogui.moveTo(722 + left, 275 + up)
		pyautogui.click()

	if action == 2:
		pyautogui.moveTo(817 + left, 275 + up)
		pyautogui.click()

	if action == 3:
		pyautogui.moveTo(905 + left, 250 + up)
		pyautogui.click()

	if action == 4:
		pyautogui.moveTo(488 + left, 250 + up)
		pyautogui.click()

	time.sleep(0.1)


def main():
	try:
		counter_card_gods_of_odds = 127
		if learn_classifier:
			#read images
			imgs = []
			for i in range(counter_card_gods_of_odds):
				#img = cv2.imread("cards/%s.jpg"%str(i))
				img = misc.imread("slots/%s.jpg"%str(i),mode='L')
				imgs.append(img.flatten())
			clf = SVC()
			clf1 =  LinearSVC()
			labels = np.zeros(counter_card_gods_of_odds)
			labels[0:6] = np.ones(6)
			labels[50:60] = 2 * np.ones(10)
			labels[8:11] = 3 * np.ones(3)
			labels[61:63] = 3 * np.ones(2)
			labels[85:87] = 4 * np.ones(2)
			labels[87:90] = 3 * np.ones(3)
			labels[90:92] = 5 * np.ones(2)
			labels[92:98] = 6 * np.ones(6)
			labels[98:100] = 4 * np.ones(2)
			labels[100:104] = 3 * np.ones(4)
			labels[104:106] = 7 * np.ones(2)
			labels[106:111] = 3 * np.ones(5)
			labels[111:116] = 6 * np.ones(5)
			labels[116:120] = 8 * np.ones(4)
			labels[120:123] = 9 * np.ones(3)
			labels[123:127] = 3 * np.ones(4)
			print 'gathered', len(imgs), len(labels)
			clf.fit(imgs,labels)
			clf1.fit(imgs,labels)

			print 'fitted'

		if online:
			pyautogui.moveTo(100 + left, 700 + up)
			pyautogui.click()
			time.sleep(0.1)

		c = 0

		while True:
			if grab_images:
				im=ImageGrab.grab(bbox=(442 + left,490 + up,552 + left,540 + up)) # X1,Y1,X2,Y2

				im.save("slots/%s.jpg"%str(counter_card_gods_of_odds))
				counter_card_gods_of_odds += 1
			rec = grab_rect(clf)
			rec1 = grab_rect(clf1)
			print c, rec,rec1
			if rec1 == 1:
				pyautogui.click(490 + left,470 + up)
				time.sleep(14)
			if rec1 == 2:
				pyautogui.click(630 + left,500 + up)
				time.sleep(10)
			if rec1 == 3:
				pyautogui.click(430 + left,590 + up)
				time.sleep(1)
				pyautogui.click(500 + left,615 + up)
				time.sleep(5)
			if rec1 == 4:
				pyautogui.click(510 + left,480 + up)
				time.sleep(1)
				pyautogui.click(567 + left,520 + up)
				time.sleep(5)
				pyautogui.click(771 + left,200 + up)
				time.sleep(5)
			if rec1 == 5:
				pyautogui.click(600 + left,555 + up)
				time.sleep(14)
			if rec1 == 6:
				pyautogui.click(510 + left,490 + up)
				time.sleep(4)
			if rec1 == 7:
				pyautogui.click(810 + left,145 + up)
				time.sleep(4)
			if rec1 == 8:
				pyautogui.click(820 + left,140 + up)
				time.sleep(4)
			if rec1 == 9:
				pyautogui.click(570 + left,540 + up)
				time.sleep(4)

			if c%10==0:
				pyautogui.click(430 + left,590 + up)
				time.sleep(1)
				pyautogui.click(500 + left,615 + up)
				time.sleep(5)
			if c%150==0:
				print 'trying other tab'
				pyautogui.click(520 + left,40)
				time.sleep(0.6)
				pyautogui.click(510 + left,605 + up)
				time.sleep(1.2)
				pyautogui.click(745 + left,530 + up)
				time.sleep(0.6)
				pyautogui.click(90 + left,40)


			pyautogui.click(800 + left,610 + up)
			time.sleep(4)

			c += 1
	except KeyboardInterrupt:
		exit(-1)
 	
if __name__ == '__main__':
    main()
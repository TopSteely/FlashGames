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

grab_images = True
learn_classifier = True
online = False

def bet():
	print 'bet'
	pyautogui.moveTo(500 + left,490 + up)
	time.sleep(0.1)
	pyautogui.click(500 + left,490 + up)

def double_down():
	print 'double'
	pyautogui.click(690 + left,610 + up)

def hit():# also newgame 
	print 'hit'
	pyautogui.click(745 + left,610 + up) 

def stand():# also rebet, deal
	print 'stand'
	pyautogui.click(800 + left,600 + up)

def split():
	print 'split'
	pyautogui.click(640 + left,610 + up)



def grab_rect(clf):
	im=ImageGrab.grab(bbox=(442 + left,490 + up,552 + left,540 + up))
	img = im.convert('L')
	img = np.asarray(img)
	card = clf.predict(img.flatten().reshape(1, -1))[0]
	return card

def view_dealer(clf_dealer1):
	im=ImageGrab.grab(bbox=(510 + left,256 + up,540 + left,280 + up)) # X1,Y1,X2,Y2
	#im.save("blackjack/d%s.jpg"%str(100))
	im = im.convert('L')
	im = np.asarray(im)
	return clf_dealer1.predict(im.flatten().reshape(1, -1))[0]


def main():
	try:
		counter_card_gods_of_odds = 100
		if learn_classifier:
			#read images
			imgs_dealer = []
			imgs_player = []
			imgs_result = []
			for i in range(13):
				#img = cv2.imread("cards/%s.jpg"%str(i))
				img = misc.imread("blackjack/d%s.jpg"%str(i),mode='L')
				imgs_dealer.append(img.flatten())
			clf_dealer1 =  LinearSVC()
			labels_dealer = range(13)
			print 'dealer gathered', len(imgs_dealer), len(labels_dealer)
			clf_dealer1.fit(imgs_dealer,labels_dealer)

			for i in range(41):
				#img = cv2.imread("cards/%s.jpg"%str(i))
				img = misc.imread("blackjack/p%s.jpg"%str(i),mode='L')
				imgs_player.append(img.flatten())
				imgs_result.append(img.flatten())
			clf_player1 =  LinearSVC()
			labels_player = range(30)
			labels_player = np.concatenate([labels_player,np.array([10,10,20,20,18,18,11,15,15,16,16])])
			labels_result = np.zeros(41)
			print 'player gathered', len(imgs_player), len(labels_player)
			clf_player1.fit(imgs_player,labels_player)

			for i in range(12):
				#img = cv2.imread("cards/%s.jpg"%str(i))
				img = misc.imread("blackjack/c%s.jpg"%str(i),mode='L')
				imgs_result.append(img.flatten())
			clf_result1 =  LinearSVC()
			labels_result = np.concatenate([labels_result,np.array([1,1,2,1,1,1,2,1,2,1,3,3])])
			print 'result gathered', len(imgs_result), len(labels_result),labels_result
			clf_result1.fit(imgs_result,labels_result)

			print 'fitted'

		if online:
			pyautogui.moveTo(100 + left, 700 + up)
			pyautogui.click()
			time.sleep(0.1)

		c = 0
		r = 1
		prev_bet = 1
		hit1 = True

		while True:
			#bet
			if r == 1:
				if prev_bet == 1:
					stand()
				else:
					print 'won'
					hit()
					time.sleep(1.0)
					bet()
					time.sleep(1.0)
					stand()
					prev_bet = 1
			elif r == 3:
				print 'push'
				stand()
			elif r == 2:
				print 'lost'
				time.sleep(0.5)
				prev_bet = 2*prev_bet
				hit()
				time.sleep(1.5)
				for x in range(prev_bet):
					print x, prev_bet
					bet()
					#bet()
					time.sleep(0.1)
				stand()
			time.sleep(0.5)
			#get dealer card
			d = view_dealer(clf_dealer1)
			time.sleep(0.5)
			if d == 12:
				pyautogui.click(770 + left,100 + up)
				time.sleep(0.5)
				hit()
				time.sleep(1.0)
				bet()
				time.sleep(1.0)
				stand()
				prev_bet = 1
				d = view_dealer(clf_dealer1)
				time.sleep(0.5)
			while d == 0:
				print 'loop', d
				d = view_dealer(clf_dealer1)
			cards = 2
			print 'dealre: ', d
			if d == 11:
				r=2
			else:

				while clf_result1.predict(np.asarray(ImageGrab.grab(bbox=(510 + left,521 + up,540 + left,545 + up)).convert('L')).flatten().reshape(1, -1))[0] == 0:
					im=ImageGrab.grab(bbox=(510 + left,521 + up,540 + left,545 + up)) # X1,Y1,X2,Y2
					im.save("blackjack/p%s.jpg"%str(counter_card_gods_of_odds))
					im = im.convert('L')
					im = np.asarray(im)
					p = clf_player1.predict(im.flatten().reshape(1, -1))[0]
					counter_card_gods_of_odds += 1
					print d,p
					#if double ace always split
					if d == 1:
						time.sleep(0.8)
						if hit1:
							hit()
							hit1 = False
							time.sleep(1.8)
						print 'player has ', p
						if p < 17:
							print '< 17'
							hit()
						elif p>21 and p<28:
							print '> 21 and <28'
							hit()
						else:
							print 'else'
							stand()

					if p == 2:
						split()
					elif p < 10:
						hit()
					elif p == 10 and d <= 7:
						if cards == 2:
							double_down()
						else:
							hit()
					elif p == 11 and d <= 8:
						if cards == 2:
							double_down()
						else:
							hit()
					elif p == 10 and d>7:
						hit()
					elif p == 11 and d>8:
						hit()
					elif p<17 and p>11 and d >= 7:
						hit()
					elif p > 16 and p < 22:
						stand()
					elif p == 29:
						stand()
					elif p>21 and p<27 and d<7:
						if cards == 2:
							double_down()
						else:
							hit()
					elif p == 26 and d == 10:
						hit()
					elif p>21 and p<26 and d>=7:
						hit()
					elif p>=26 and p<29 and d<9:
						stand()
					elif p>21 and p<28 and d==9:
						hit()
					elif p==28 or p==29 and d==9:
						stand()
					elif p>21 and p<29 and d==10:
						stand()
					elif d < 7:
						stand()
					elif p == 18 or p == 19 or p == 20:
						stand()
					else:
						print d,p,'exit'
						exit(-1)

					cards += 1
					time.sleep(0.9)

				r = clf_result1.predict(np.asarray(ImageGrab.grab(bbox=(510 + left,521 + up,540 + left,545 + up)).convert('L')).flatten().reshape(1, -1))[0]
			print r
			time.sleep(1.4)
			hit1 = True
	except KeyboardInterrupt:
		exit(-1)
 	
if __name__ == '__main__':
    main()
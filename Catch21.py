#from selenium import webdriver

#from pyvirtualdisplay import Display
import pyautogui
import time
import pyscreenshot as ImageGrab
import matplotlib.pyplot as plt
from sklearn.svm import SVC
#import cv2

from scipy import misc
#from utils import *
from Q_learning import *
from draw_step import *

left = 56
up = 88

grab_images = True
learn_classifier = False
online = True
learn_game = False

#spade = s
#hearts = h
#diamonds = d
#clubs = c
#king = 13
#queen = 12
#jack = 11

def grab_card(clf):
	im=ImageGrab.grab(bbox=(348 + left,212 + up,418 + left,308 + up))
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

def get_labels():
	labels = ["8d","4c","2h","8s","7d","7s","3s","1s","5d","10h","3h",
	"4d","4s","1d","13d","6h","5c","12s","13c","10s","6s","12d",
	"11s","11h","3d","5s","10c","13s","9h","8c","13h","9d","2c",
	"11c","1h","7c","5h","2s","8h","6d","1c","3c","2d","9s","7h",
	"4h","10d","12h","6c","11d","12c","9c",]
	return labels


def main():
	try:
		#display = Display(visible=0, size=(1024, 768))
		#display.start()
		# Firefox ain't got no Flash
		#browser = webdriver.Chrome()
		#browser.maximize_window()
		#actions = ActionChains(browser)
		#browser.get('https://www.worldwinner.com/cgi/tournament/list_single.pl?game_id=83&LinkTrack=Home_catch21&as=4')
		# wait for the page to load
		#time.sleep(60)

		#move to login
		#pyautogui.moveTo(955 + left, 131 + up)
		#pyautogui.click()
		#time.sleep(2)
		#pyautogui.moveTo(530 + left, 297 + up)
		#pyautogui.click()
		#pyautogui.typewrite('mypuser176304567.myp')
		##time.sleep(2)
		#pyautogui.moveTo(525 + left, 319 + up)
		#pyautogui.click()
		#pyautogui.typewrite('Slayer24')
		##time.sleep(5)
		#pyautogui.moveTo(537 + left, 368 + up)
		#pyautogui.click()

		if learn_classifier:
			#read images
			imgs = []
			for i in range(52):
				img = misc.imread("cards/%s.jpg"%str(i),mode='L')
				imgs.append(img.flatten())
			print 'gathered'
			clf = SVC(verbose=True)
			labels = get_labels()
			clf.fit(imgs,labels)

			print 'fitted'

			#test - working
			#for i in [1,4,7,9,14]:
			#	img = misc.imread("cards/%s.jpg"%str(i),mode='L')
			#	plt.imshow(img)
			#	plt.show()
			#	print clf.predict(img.flatten().reshape(1, -1))

		if online:
			pyautogui.moveTo(100 + left, 100 + up)
			pyautogui.click()
			time.sleep(0.5)
			pyautogui.moveTo(536 + left, 292 + up)
			pyautogui.click()
			time.sleep(4)
			pyautogui.moveTo(747 + left, 405 + up)
			pyautogui.click()
			time.sleep(0.1)
		if grab_images:
			time.sleep(1)
			for i in range(52):
				im=ImageGrab.grab(bbox=(348 + left,212 + up,418 + left,308 + up)) # X1,Y1,X2,Y2

				im.save("catch22/%s.jpg"%str(i))
				pyautogui.moveTo(488 + left, 250 + up)
				pyautogui.click()
				time.sleep(0.4)

		if learn_game:
			Q_Learning_simulation(1000000, 10000)

		policy = Q_Learning_Control()
		policy.Q.load_from_buffer('Q_Learning_Q.npy')
		policy.set_in_use(True)

		card = grab_card(clf)
		print card
		state = State(card, 0, None, [], [], [], [])
		time.sleep(0.1)

		policy.start_new_episode()
		cards_ind = 0
		while cards_ind<53:
			action = policy.next_action(state)
			move(action)
			card = grab_card(clf)
			print card
			state_new = step(state, action, card)
			reward = get_reward_from_state(state_new)
			policy.update_policy_online(state, state_new, action, reward)
			state = state_new
			cards_ind += 1

		#browser.save_screenshot("test")
		#time.sleep(460)
		#browser.close()
		#display.close()
	except Exception as e:
		print e.message
 	
if __name__ == '__main__':
    main()
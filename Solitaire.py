#webrownus

#from selenium import webdriver

#from pyvirtualdisplay import Display
import pyautogui
import time
import pyscreenshot as ImageGrab
import matplotlib.pyplot as plt
from sklearn.svm import SVC
from sklearn.svm import LinearSVC
#import cv2
import copy
import pickle
import math

from scipy import misc
#from utils import *
from Q_learning import *
from draw_step import *
import numpy as np
import Tkinter as tk

left = 65
up = 87
card_width = 71
card_height = 96
stack_ = 20
card_over_card = 22

grab_images = True
learn_classifier = False
online = False
gather_stacksize = False
gather_cards = True
sleep_time_draw = 0.4# 0.4 seems to be too fast sometimes
sleep_time_stack = 0.3

debug_show = False

counter_draws = 0

three_draw = True

if three_draw:
	div = 3.0
	dontplay59 = False
	stop_crit = 1
else:
	div = 1.0
	dontplay59 = True
	stop_crit = 1

def draw_card(clf_cards,clf_color,num_draw_cards, counter_draws):
	if num_draw_cards == 0:
		num_draw_cards = 1
	im=ImageGrab.grab(bbox=(918 - 18 * (3 - num_draw_cards) + left,154 + up,918 - 18 * (3 - num_draw_cards) + left + card_width,154 + up + card_height))
	img = im.convert('L')
	img = np.asarray(img)
	im.convert('RGB').save("solitaire/draws/%s_%s.jpg"%(str(counter_draws),str(num_draw_cards)))
	card = [clf_cards.predict(img[2:,:-4].flatten().reshape(1, -1))[0],clf_color.predict(img[2:,:-4].flatten().reshape(1, -1))[0]]
	np.savetxt("solitaire/draws/%s_%s.txt"%(str(counter_draws),str(num_draw_cards)), [card], fmt='%s')
	counter_draws += 1
	return card, counter_draws

def grab_rect(clf):
	im=ImageGrab.grab(bbox=(442 + left,490 + up,552 + left,540 + up))
	img = im.convert('L')
	img = np.asarray(img)
	card = clf.predict(img.flatten().reshape(1, -1))[0]
	return card

def drag(pos1,pos2, stack, num_cards, ix = 0):
	if stack[pos1] < 0:
		tmp = 0
	else:
		tmp = stack[pos1]
	if stack[pos2] < 0:
		tmp1 = 0
	else:
		tmp1 = stack[pos2]
	#drag from pos 1 to pos 2
	#pyautogui.moveTo((pos1*(card_width+stack_))+336 + 40 + left, 268 + 4*tmp + up + 3 + 4 * num_cards[pos1])
	#changed to
	pyautogui.moveTo((pos1*(card_width+stack_))+336 + 40 + left, 268 + 4*tmp + up + 2 + ix * 22)
	pyautogui.dragTo((pos2*(card_width+stack_))+336 + 40 + left, 268 + 4*tmp1 + up + 40 + 22 * num_cards[pos2], button='left', duration=0.2)

def drag1(pos1,pos2, stack, num_cards):
	if pos1 == 0:
		pos1 = 1
	if stack[pos2] < 0:
		tmp1 = 0
	else:
		tmp1 = stack[pos2]
	#drag from pos 1 to pos 2
	pyautogui.moveTo((pos1-1)*18 + 890 + 40 + left, 195 + up)
	pyautogui.dragTo((pos2*(card_width+stack_))+336 + 40 + left, 268 + 4*tmp1 + up + 40 + 22 * num_cards[pos2], button='left', duration=0.2)


def othercolor(c1,c2):
	if (c1 == 's' or c1 == 'c' or c1 == 'a') and (c2 == 'h' or c2 == 'd' or c2 == 'a'):
		return True
	elif (c2 == 's' or c2 == 'c' or c2 == 'a') and (c1 == 'h' or c1 == 'd' or c1 == 'a'):
		return True
	else:
		return False

def othersymbolsamecolor(c1):
	if (c1 == 's'):
		return 'c'
	elif (c1 == 'c'):
		return 's'
	elif (c1 == 'd'):
		return 'h'
	elif (c1 == 'h'):
		return 'd'
	elif (c1 == 'a'):
		return 'k'
	else:
		print 'wrong symbol othersymbolsamecolor'
		exit(-1)

def otherscolor(c1):
	if (c1 == 's'):
		return 'h','d'
	elif (c1 == 'c'):
		return 'h','d'
	elif (c1 == 'd'):
		return 's','c'
	elif (c1 == 'h'):
		return 's','c'
	elif (c1 == 'a'):
		return 'k'
	else:
		print 'wrong symbol otherscolor'
		exit(-1)

def next_card_protected(aces,stacks,c):
	#either same color card on board
	all_cards = [x for b in stacks.values() for x in b]
	if [c[0],othersymbolsamecolor(c[1])] in all_cards:
		return True
	kk = otherscolor(c[1])
	#next lowest cards already on board
	if [c[0]-1,kk[0]] in all_cards and [c[0]-1,kk[1]] in all_cards:
		return True
	#next lowest cards already on aces
	all_cards = [x for b in aces.values() for x in b]
	if [c[0]-1,kk[0]] in all_cards and [c[0]-1,kk[1]] in all_cards:
		return True
	return False

def playable(play_card, stacks, aces):
	if [play_card[0] - 1, play_card[1]] in [x for b in aces.values() for x in b]:
		print 'playable in ace'
		return True
	if [play_card[0] + 1,otherscolor(play_card[1])[0]] in [x[-1] for x in stacks.values()] or [play_card[0] + 1,otherscolor(play_card[1])[0]] in [x[-1] for x in stacks.values()]:
		print 'playable in stacks'
		return True
	return False

def play_to_free(play_card, stacks, aces, sts, num_cards):
	print 'in play'
	if [play_card[0] - 1, play_card[1]] in [x for b in aces.values() for x in b]:
		#find play_card
		stack_ind = [ix for ix,b in enumerate(stacks.values()) for x in b if x == play_card][0]
		ind = stacks[stack_ind].index(play_card)
		sts, aces, num_cards, stacks = click_(sts,stack_ind, aces, play_card, num_cards, stacks)
		return sts, aces, num_cards, stacks

	if [play_card[0] + 1,otherscolor(play_card[1])[0]] in [x[-1] for x in stacks.values()] or [play_card[0] + 1,otherscolor(play_card[1])[0]] in [x[-1] for x in stacks.values()]:
		print 'playable in stacks'
		exit(-1)
def click_(sts,stck_i, aces, card, num_cards, stack_cards):
	if sts[stck_i] < 0:
		tmp = 0
	else:
		tmp = sts[stck_i]
	print 'in click', tmp, num_cards[stck_i]
	pyautogui.moveTo((stck_i*(card_width+stack_)) + 337 + left + 10,268 + 22 * (num_cards[stck_i]-1) + 4*tmp + up + 10)
	pyautogui.click()
	time.sleep(0.1)
	pyautogui.click()
	time.sleep(0.4)
	click = False
	moved = True

	#find color and add
	aces[[x[0] for x in aces.values()].index([1,card[1]])].append(card)
	#remove from stack
	del stack_cards[stck_i][-1]
	num_cards[stck_i] -= 1
	if num_cards[stck_i] == 0:
		sts[stck_i] -= 1
	return sts, aces, num_cards, stack_cards

def main():
	try:
		#pyautogui.moveTo(100 + left, 100 + up)
		#pyautogui.click()
		counter_card_gods_of_odds = 13
		counter_stacksize = 22
		counter_cards = 185
		counter_draws = 0
		counter_whenace = 0
		counter_second = 0
		counter_cards_copy = counter_cards
		num_cards = [1,1,1,1,1,1,1]

		imgs_cards = []
		h = 'h'
		s = 's'
		c = 'c'
		d = 'd'
		print 'start'
		if learn_classifier:
			clf_cards =  LinearSVC()
			clf_color =  LinearSVC()
			for i in range(counter_cards_copy):
				img = misc.imread("solitaire/cards/%s.jpg"%str(i),mode='L')
				if debug_show:
					print img.shape
					plt.imshow(img)
					plt.show()
					plt.figure()
					plt.imshow(img[2:,:-4])
					plt.show()
					raw_input()
				imgs_cards.append(img[2:,:-4].flatten())
			labels_cards = [1,7,2,13,8,6,8,12,10,13,2,7,12,4,9,8,7,10,4,9,6,8,9,3,7,12,11,9,11,13,13,7,12,11,3,5,6,13,5,4,10,3,11,8,6,2,5,13,7,12,8,3,11,1,6,11,6,13,12,8,7,13,4,6,3,1,5,2,2,4,3,12,7,6,9,5,8,1,13,3,12,9,5,11,7,10,9,3,7,9,8,1,8,12,10,4,5,6,11,13,6,7,2,7,10,6,13,4,9,12,13,10,3,5,10,9,9,11,8,8,12,10,6,5,4,12,13,6,2,7,2,5,4,11,5,9,8,4,5,6,11,13,6,7,9,10,11,6,2,5,6,1,8,1,7,2,13,8,6,8,2,7,10,6,13,4,9,11,8,1,4,10,5,7,6,3,7,9,3,5,11,8,13,13,13]
			labels_color = [h,s,s,d,h,s,c,c,h,h,h,h,d,d,s,s,c,d,h,d,d,c,h,s,s,c,s,s,h,h,d,h,h,s,s,h,c,d,c,c,d,c,d,s,s,d,s,s,d,d,s,c,c,s,s,s,h,s,h,s,h,h,h,s,h,h,s,s,h,c,h,s,h,c,h,d,s,h,c,s,h,s,d,c,h,s,d,s,c,s,c,c,d,h,h,d,d,h,s,h,s,d,s,h,s,c,d,c,h,s,d,s,c,d,h,s,c,s,h,c,h,h,s,h,c,s,h,d,c,c,c,c,s,d,h,c,h,d,d,h,s,h,s,d,d,h,s,h,d,h,c,d,d,h,s,s,d,h,s,c,s,h,s,c,d,c,h,h,c,h,d,c,h,d,s,d,d,c,c,h,h,h,c,d,s]
			print len(labels_cards), len(labels_color)
			clf_cards.fit(imgs_cards,labels_cards)
			clf_color.fit(imgs_cards,labels_color)

			pickle.dump( clf_cards, open( "clf_cards.p", "wb" ) )
			pickle.dump( clf_color, open( "clf_color.p", "wb" ) )
		else:
			clf_cards = pickle.load( open( "clf_cards.p", "rb" ) )
			clf_color = pickle.load( open( "clf_color.p", "rb" ) )

		print 'done'

		stack_cards = {0:[],1:[],2:[],3:[],4:[],5:[],6:[]}
		#hack
		aces = {0:[0],1:[0],2:[0],3:[0]}
		num_aces = 0

		history = []
		rounds = 0

		remaining_draw_cards = 24
		remaining_draw_cards_tmp = 24
		sts = [0,1,2,3,4,5,6]
		no_moves = 0
		not_moved = True

		click = True
		pyautogui.moveTo(810 + left, 180 + up)
		pyautogui.click()
		if three_draw:
			draw_cards = 3
			next_draw = 3
		else:
			draw_cards = 1
			next_draw = 1
		triples = 0
		for i in range(7):
			im=ImageGrab.grab(bbox=((i*(card_width+stack_)) + 337 + left,268 + 22 * (num_cards[i]-1) + 4*sts[i] + up,(i*(card_width+stack_))+337 + card_width + left,4*sts[i] + 268 + card_height + up + 22 * (num_cards[i]-1)))
			if gather_cards:
				im.convert('RGB').save("solitaire/cards/%s.jpg"%str(counter_cards))
				counter_cards += 1
			img = im.convert('L')
			img = np.asarray(img)
			stack_cards[i].append( [clf_cards.predict(img[2:,:-4].flatten().reshape(1, -1))[0], clf_color.predict(img[2:,:-4].flatten().reshape(1, -1))[0]] )

		moved = True
		
		cards_seen = 0
		draw_cards_used = 0

		continue_to_draw = False

		while True:
			#strategy
			#1. Always play an Ace or Deuce wherever you can immediately.
			#stack_cards

			#2. Always make the play or transfer that frees (or allows a play that frees) a downcard, regardless of any other considerations.
			i = 6
			moved = False
			#pyautogui.moveTo(810 + left, 180 + up)
			#pyautogui.click()
			while not moved and i >= 0:
				##print 'just for error: ',  stack_cards.values()
				sorted_sts = [j[0] for j in sorted(enumerate(sts), key=lambda x:x[1])]
				stck_i = sorted_sts[i]
				just_numbers = [x[-1][0] for x in stack_cards.values()]
				for_king = [x[0][0] for x in stack_cards.values()]

				card = stack_cards[stck_i][0]

				all_cards = [x for b in stack_cards.values() for x in b]
				#print sts, stack_cards
				if num_cards[stck_i] == 0:
					print 'thats why! 1'
					pass
				elif card[0] == 1:
					print 'thats why! 2'
					pyautogui.moveTo((stck_i*(card_width+stack_)) + 337 + left + 10,268 + 22 * (num_cards[stck_i]-1) + 4*sts[stck_i] + up + 10)
					pyautogui.click()
					time.sleep(0.1)
					pyautogui.click()
					aces[num_aces] = [card]
					num_aces += 1
					sts[stck_i] -= 1
					if sts[stck_i] >= 0:
						time.sleep(sleep_time_stack)
						im=ImageGrab.grab(bbox=((stck_i*(card_width+stack_)) + 337 + left,268 + 4*sts[stck_i] + up,(stck_i*(card_width+stack_))+337 + card_width + left,4*sts[stck_i] + 268 + card_height + up))
						img = im.convert('L')
						img = np.asarray(img)
						im.convert('RGB').save("solitaire/debug/whenace%s.jpg"%str(counter_whenace))
						stack_cards[stck_i] = [[clf_cards.predict(img[2:,:-4].flatten().reshape(1, -1))[0], clf_color.predict(img[2:,:-4].flatten().reshape(1, -1))[0]]]
						np.savetxt("solitaire/debug/whenace%s.txt"%str(counter_whenace), [stack_cards[stck_i]], fmt='%s')
						counter_whenace += 1
						num_cards[stck_i] = 1
					else:
						stack_cards[stck_i] = [[14,'a']]
						num_cards[stck_i] = 0
					moved = True
					click = False
				elif card[0] == 2 and [1,card[1]] in [x[0] for x in aces.values()]:
					print 'thats why! 3'
					print 'in cards[0]==2', card
					pyautogui.moveTo((stck_i*(card_width+stack_)) + 337 + left + 10,268 + 22 * (num_cards[stck_i]-1) + 4*sts[stck_i] + up + 10)
					pyautogui.click()
					time.sleep(0.1)
					pyautogui.click()
					sts[stck_i] -= 1

					#find color and add
					aces[[x[0] for x in aces.values()].index([1,card[1]])].append(card)
					#remove from stack
					#changed from 0 to 1, confirm?
					if sts[stck_i] >= 0:
						time.sleep(sleep_time_stack)
						im=ImageGrab.grab(bbox=((stck_i*(card_width+stack_)) + 337 + left,268 + 4*sts[stck_i] + up,(stck_i*(card_width+stack_))+337 + card_width + left,4*sts[stck_i] + 268 + card_height + up))
						img = im.convert('L')
						img = np.asarray(img)
						im.convert('RGB').save("solitaire/debug/second1%s.jpg"%str(counter_second))
						counter_second += 1
						stack_cards[stck_i] = [[clf_cards.predict(img[2:,:-4].flatten().reshape(1, -1))[0], clf_color.predict(img[2:,:-4].flatten().reshape(1, -1))[0]]]
						np.savetxt("solitaire/debug/second1%s.txt"%str(counter_second), [stack_cards[stck_i]], fmt='%s')
						num_cards[stck_i] = 1
						# not needed because it's only if it's the first card
						#del stack_cards[i][-1]
						#num_cards[i] -= 1
					else:
						stack_cards[stck_i] = [[14,'a']]
						num_cards[stck_i] = 0

					moved = True
					click = False
				elif sts[stck_i] == 0 and 13 not in for_king:
					print 'thats why! 4'
					pass
				elif card[0] == 13 and sts[stck_i] <= 0:
					print 'thats why! 5'
					#don't move king to another empty field
					print 'not moving king'
					pass
				elif card[0] + 1 in just_numbers and (sts[stck_i] > 0 or (13 in for_king and any([sts[ki]>0 for ki,xtthr in enumerate(for_king) if xtthr==13]))):
					print 'thats why! 6'
					indices = [ir for ir, x in enumerate(just_numbers) if x == card[0] + 1]
					for ic in indices:
						if othercolor(card[1],stack_cards[ic][-1][1]):
							drag(stck_i,ic,sts,num_cards)
							stack_cards[ic].extend(stack_cards[stck_i])
							num_cards[ic] += len(stack_cards[stck_i])
							sts[stck_i] -= 1

							if sts[stck_i] >= 0:
								time.sleep(sleep_time_stack)
								im=ImageGrab.grab(bbox=((stck_i*(card_width+stack_)) + 337 + left,268 + 4*sts[stck_i] + up,(stck_i*(card_width+stack_))+337 + card_width + left,4*sts[stck_i] + 268 + card_height + up))
								img = im.convert('L')
								img = np.asarray(img)
								im.convert('RGB').save("solitaire/debug/second2%s.jpg"%str(counter_second))
								stack_cards[stck_i] = [[clf_cards.predict(img[2:,:-4].flatten().reshape(1, -1))[0], clf_color.predict(img[2:,:-4].flatten().reshape(1, -1))[0]]]
								np.savetxt("solitaire/debug/second2%s.txt"%str(counter_second), [stack_cards[stck_i]], fmt='%s')
								num_cards[stck_i] = 1
								counter_second += 1
							else:
								stack_cards[stck_i] = [[14,'a']]
								num_cards[stck_i] = 0

							moved = True
							click = False
							break
				if not moved and [card[0] - 1,card[1]] in [x[-1] for x in aces.values()] and num_cards[stck_i] == 1:
					print 'are we going here? 1111'
					pyautogui.moveTo((stck_i*(card_width+stack_)) + 337 + left + 10,268 + 22 * (num_cards[stck_i]-1) + 4*sts[stck_i] + up + 10)
					pyautogui.click()
					time.sleep(0.1)
					pyautogui.click()
					sts[stck_i] -= 1

					#find color and add
					aces[[x[0] for x in aces.values()].index([1,card[1]])].append(card)
					#remove from stack
					#changed from 0 to 1, confirm?
					if sts[stck_i] >= 0:
						time.sleep(sleep_time_stack)
						im=ImageGrab.grab(bbox=((stck_i*(card_width+stack_)) + 337 + left,268 + 4*sts[stck_i] + up,(stck_i*(card_width+stack_))+337 + card_width + left,4*sts[stck_i] + 268 + card_height + up))
						img = im.convert('L')
						img = np.asarray(img)
						im.convert('RGB').save("solitaire/debug/second3%s.jpg"%str(counter_second))
						counter_second += 1
						stack_cards[stck_i] = [[clf_cards.predict(img[2:,:-4].flatten().reshape(1, -1))[0], clf_color.predict(img[2:,:-4].flatten().reshape(1, -1))[0]]]
						np.savetxt("solitaire/debug/second3%s.txt"%str(counter_second), [stack_cards[stck_i]], fmt='%s')
						num_cards[stck_i] = 1
						# not needed because it's only if it's the first card
						#del stack_cards[i][-1]
						#num_cards[i] -= 1
					else:
						stack_cards[stck_i] = [[14,'a']]
						num_cards[stck_i] = 0

					moved = True
					click = False
				elif not moved and [card[0] - 1,card[1]] in [x[-1] for x in aces.values()] and [card[0],othersymbolsamecolor(card[1])] in all_cards and num_cards[stck_i] == 1:
					print 'does this ever happen?' #no
					exit()
					for ix in stack_cards:
						if [card[0],othersymbolsamecolor(card[1])] in stack_cards[ix]:
							ind = stack_cards[ix].index([card[0],othersymbolsamecolor(card[1])])
					if ind+1 > num_cards[ix]:
						pass
					else:
						print 'dragging ', stack_cards[ix][ind+1:], ' to ', stack_cards[stck_i]
						drag(ix,stck_i, sts, num_cards, ind + 1)
						stack_cards[stck_i].extend(stack_cards[ix][ind+1:])
						num_cards[stck_i] += len(stack_cards[ix][ind+1:])
						num_cards[ix] -= len(stack_cards[ix][ind+1:])
						del stack_cards[ix][ind+1:]
						moved = True
						click = False
				elif not moved and [card[0] - 1,othersymbolsamecolor(card[1])] in [x[-1] for x in aces.values()] and [card[0],othersymbolsamecolor(card[1])] in all_cards and num_cards[stck_i] == 1 and sts[stck_i] > 0:
					print card, [card[0] - 1,othersymbolsamecolor(card[1])], [card[0],othersymbolsamecolor(card[1])]
					for ix in stack_cards:
						if [card[0],othersymbolsamecolor(card[1])] in stack_cards[ix]:
							ind = stack_cards[ix].index([card[0],othersymbolsamecolor(card[1])])
							break
					if ind+1 > num_cards[ix]:
						pass
					else:
						#TODO!!!!!


						#first
						pyautogui.moveTo((ix*(card_width+stack_)) + 337 + left + 10,268 + 22 * (num_cards[ix]-1) + 4*sts[ix] + up + 10)
						pyautogui.click()
						time.sleep(0.1)
						pyautogui.click()
						num_cards[ix] -= 1
						if num_cards[ix] == 0:
							stack_cards[ix] = [[14,'a']]

						#then
						#print 'dragging ', stack_cards[ix][ind+1:],' from ', ix, ' to ', stack_cards[stck_i], ' to free ', card
						#drag(stck_i, ix, sts, num_cards, ind + 1)
						#stack_cards[stck_i].extend(stack_cards[ix][ind+1:])
						#num_cards[stck_i] += len(stack_cards[ix][ind+1:])
						#num_cards[ix] -= len(stack_cards[ix][ind+1:])
						#del stack_cards[ix][ind+1:]

						moved = True
						click = False

						#print 'done?'
						#exit()

				card = stack_cards[stck_i][-1]
				if card[0] == 2 and [1,card[1]] in [x[0] for x in aces.values()] and num_cards[stck_i] != 1:
					print 'in last stack_cards[stck_i][-1] == 2'
					if sts[stck_i] < 0:
						tmp = 0
					else:
						tmp = sts[stck_i]
					pyautogui.moveTo((stck_i*(card_width+stack_)) + 337 + left + 10,268 + 22 * (num_cards[stck_i]-1) + 4*tmp + up + 10)
					pyautogui.click()
					time.sleep(0.1)
					pyautogui.click()

					#find color and add
					aces[[x[0] for x in aces.values()].index([1,card[1]])].append(card)
					#remove from stack
					del stack_cards[stck_i][-1]
					num_cards[stck_i] -= 1
					if num_cards[stck_i] == 0:
						stack_cards[stck_i] = [[14,'a']]

					click = False
					moved = True

				if not moved and next_card_protected(aces,stack_cards,card) and [card[0] - 1,card[1]] in [x[-1] for x in aces.values()] and num_cards[stck_i] != 1:
					print 'in if next_card_protected', card
					print sts, num_cards
					if all([x<=0 for x in sts]):
						print 'now we should just play draw_cards!, right?'
						continue_to_draw = True
					if not continue_to_draw:
						if sts[stck_i] < 0:
							tmp = 0
						else:
							tmp = sts[stck_i]
						pyautogui.moveTo((stck_i*(card_width+stack_)) + 337 + left + 10,268 + 22 * (num_cards[stck_i]-1) + 4*tmp + up + 10)
						pyautogui.click()
						time.sleep(0.1)
						pyautogui.click()
						time.sleep(0.4)
						click = False
						moved = True

						print 'did this go well?'

						#find color and add
						aces[[x[0] for x in aces.values()].index([1,card[1]])].append(card)
						#remove from stack
						del stack_cards[stck_i][-1]
						num_cards[stck_i] -= 1
						if num_cards[stck_i] == 0:
							sts[stck_i] -= 1
						
						end_moved = True
						if sts[stck_i] >= 0 and num_cards[stck_i] == 0:
							time.sleep(sleep_time_stack)
							im=ImageGrab.grab(bbox=((stck_i*(card_width+stack_)) + 337 + left,268 + 4*sts[stck_i] + up,(stck_i*(card_width+stack_))+337 + card_width + left,4*sts[stck_i] + 268 + card_height + up))
							img = im.convert('L')
							img = np.asarray(img)
							im.convert('RGB').save("solitaire/debug/second2%s.jpg"%str(counter_second))
							stack_cards[stck_i] = [[clf_cards.predict(img[2:,:-4].flatten().reshape(1, -1))[0], clf_color.predict(img[2:,:-4].flatten().reshape(1, -1))[0]]]
							np.savetxt("solitaire/debug/second2%s.txt"%str(counter_second), [stack_cards[stck_i]], fmt='%s')
							num_cards[stck_i] = 1
							counter_second += 1
						print 'in last: ', num_cards[stck_i], stack_cards
						if num_cards[stck_i] == 0:
							stack_cards[stck_i] = [[14,'a']]
							#num_cards[i] = 0

				if not moved and not continue_to_draw and [2,card[1]] in [x for b in aces.values() for x in b] and sts[stck_i] > 0:#and num_cards[stck_i] == 1
					print 'is this not all true? ', card, [card[0] - 1,card[1]], [card[0] - 1,card[1]] in [x[-1] for x in aces.values()], num_cards[stck_i] == 1, [card[0] - 1,card[1]] in [x[-1] for x in aces.values()] and num_cards[stck_i] == 1
					print 'card, stck_i', card, stck_i, stack_cards[stck_i]
					for stack_card in stack_cards[stck_i]:
						# check if it's possible to free downcard by bringing in between cards to foundation
						# find highest card of that suit on foundation
						if [1,stack_card[1]] in [x for b in aces.values() for x in b]:
							ind = [ix for ix,b in enumerate(aces.values()) for x in b if x == [1,stack_card[1]]][0]
							highest = aces.values()[ind][-1]

							play_all = True
							print card, 'to check: ', range(highest[0]+1,stack_card[0]),len(range(highest[0]+1,stack_card[0])),len(range(highest[0]+1,stack_card[0]))==0
							if len(range(highest[0]+1,stack_card[0])) == 0:
								print 'should just put it on top?'
								print 'should never go here'
								print card, stack_card, range(highest[0]+1,stack_card[0])
								exit()
							else:
								for xx in range(highest[0]+1,stack_card[0]):
									# in other stacks?
									print 'looking for ', [xx, stack_card[1]], [xx, stack_card[1]] in all_cards
									if [xx, stack_card[1]] in all_cards:
										# find card
										print '1', [b for ix,b in enumerate(stack_cards.values())]
										print ' ', [xx, stack_card[1]]
										stack_ind = [ix for ix,b in enumerate(stack_cards.values()) for x in b if x == [xx, stack_card[1]]][0]
										print '2', stack_ind, [xx,stack_card[1]], stack_cards[stack_ind], stack_cards[stack_ind].index([xx,stack_card[1]])
										ind = stack_cards[stack_ind].index([xx,stack_card[1]])
										print '3', xx, stack_ind, ind
										# what has to be done to free 
										for car in stack_cards[stack_ind][ind:]:
											print car
											if not playable(car, stack_cards, aces):
												play_all = False
												break
									else:
										play_all = False
									if not play_all:
										break
						else:
							play_all = False
						print 'play all?', card, play_all
						if not play_all:
								break
						#raw_input()
					if play_all:
						print 'possible to play all!', range(highest[0]+1,card[0])
						raw_input()
						for xx in range(highest[0]+1,card[0]):
							print 'playing all, ', xx, card[0]
							print [ix for ix,b in enumerate(stack_cards.values()) for x in b if x == [xx, card[1]]]
							stack_ind = [ix for ix,b in enumerate(stack_cards.values()) for x in b if x == [xx, card[1]]][0]
							ind = stack_cards[stack_ind].index([xx,card[1]])
							print 'card', xx, stack_ind, ind
							for car in stack_cards[stack_ind][ind:]:
									sts, aces, num_cards, stack_cards = play_to_free(car, stack_cards, aces, sts, num_cards)
						raw_input()
						click = False
						moved = True

				if continue_to_draw:
					i = -1
				else:
					if moved:
						i = 6
					else:
						i -= 1

			while not moved and remaining_draw_cards_tmp > 0:
				if click or (triples == 0 and draw_cards == 0) or (cards_seen==draw_cards_used and cards_seen!=0):
					pyautogui.moveTo(810 + left, 180 + up)
					pyautogui.click()
					triples += 1
					#print 'in click: ', math.floor((remaining_draw_cards-1)/3.0), triples, math.floor((remaining_draw_cards-1)/3.0) > triples-1, remaining_draw_cards - (cards_seen)
					if math.floor((remaining_draw_cards-1)/div) > triples-1:
						if three_draw:
							if remaining_draw_cards - (cards_seen) >= 3:
								next_draw = 3
							else:
								next_draw = (remaining_draw_cards)%3 if (remaining_draw_cards)%3>0 else 3
						else:
							next_draw = 1
						cards_seen += next_draw
						draw_cards = next_draw
						s = '#3: ', remaining_draw_cards,remaining_draw_cards_tmp, cards_seen, next_draw, 'not last one'
						#print s
						#tex.insert(tk.END, s)
						#tex.see(tk.END)
						time.sleep(sleep_time_draw)
						
					elif math.floor((remaining_draw_cards-1)/div) == triples-1:
						time.sleep(0.32)
						pyautogui.moveTo(810 + left, 180 + up)
						pyautogui.click()
						rounds += 1
						triples = 0
						draw_cards_used = 0
						remaining_draw_cards = remaining_draw_cards_tmp
						if three_draw:
							draw_cards = 3 if remaining_draw_cards_tmp >= 3 else remaining_draw_cards_tmp
						else:
							draw_cards = 1
						cards_seen = draw_cards
						s = '#2: ', remaining_draw_cards_tmp, draw_cards, 'first one'
						#print s
						#tex.insert(tk.END, s)
						#tex.see(tk.END)
						not_moved = True
						time.sleep(sleep_time_draw)
				card, counter_draws = draw_card(clf_cards,clf_color,draw_cards, counter_draws)
				print card
				if card == [2, 'd']:
					time.sleep(sleep_time_draw)
					card, counter_draws = draw_card(clf_cards,clf_color,draw_cards, counter_draws)
				if rounds == 0 and card not in history and not three_draw:
					history.append(card)
					print history
				elif card not in history and three_draw:
					
					history.append(card)
					print 'h: ', history

				just_numbers = [x[-1][0] for x in stack_cards.values()]
				if card[0] == 1:
					if draw_cards == 0:
						pyautogui.moveTo(918 - 18 * (3 - 1) + left + 10,154 + up + 10)
					else:
						pyautogui.moveTo(918 - 18 * (3 - draw_cards) + left + 10,154 + up + 10)
					pyautogui.click()
					time.sleep(0.1)
					pyautogui.click()
					aces[num_aces] = [card]
					num_aces += 1
					click = False
					moved = True
					remaining_draw_cards_tmp -= 1
					draw_cards_used += 1
					if draw_cards != 0:
						draw_cards -= 1
					history.remove(card)
				elif card[0] == 2 and [1,card[1]] in [x[0] for x in aces.values()]:
					if draw_cards == 0:
						pyautogui.moveTo(918 - 18 * (3 - 1) + left + 10,154 + up + 10)
					else:
						pyautogui.moveTo(918 - 18 * (3 - draw_cards) + left + 10,154 + up + 10)
					pyautogui.click()
					time.sleep(0.1)
					pyautogui.click()

					#find color and add
					aces[[x[0] for x in aces.values()].index([1,card[1]])].append(card)
					remaining_draw_cards_tmp -= 1
					click = False
					moved = True
					draw_cards_used += 1
					if draw_cards != 0:
						draw_cards -= 1
					history.remove(card)
				elif card[0] == 13:
					all_false = True
					#are there any queens?
					indices_queens = [ir for ir, x in enumerate(stack_cards.values()) if x[0][0] == 12]
					indices_empty = [ir for ir, x in enumerate(stack_cards.values()) if x[0][0] == 14]
					#queen with the most hidden cards
					sorted_sts = [j[0] for j in sorted(enumerate(sts), key=lambda x:x[1])]
					print 'queens: ', indices_queens
					if indices_queens != []:
						if len(indices_queens)>1 and othercolor(stack_cards[indices_queens[0]][0][1],stack_cards[indices_queens[1]][0][1]):
								play = True
						elif len(indices_queens) > 2:
								play = True
						else: 
							queen_inds = []
							for xx in sorted_sts:
								if xx in indices_queens:
									queen_inds.append(xx)
							play = True
							for queen_ind in queen_inds:
								if othercolor(card[1],stack_cards[queen_ind][0][1]) or len(indices_empty) >= 2:
									print 'play'
								else:
									if [13,otherscolor(stack_cards[queen_ind][0][1])[0]] in history or [13,otherscolor(stack_cards[queen_ind][0][1])[1]] in history or (rounds == 0 and cards_seen<24):
										click = True
										play = False
										print ' dont play', [13,otherscolor(stack_cards[queen_ind][0][1])[0]] in history, [13,otherscolor(stack_cards[queen_ind][0][1])[1]] in history, (rounds == 0 and cards_seen<24)
						if any(x<=0 for x in num_cards):
							play = True
					else:
						play = True
					print play, click, moved, indices_queens
					if play:
						all_false = True
						if 14 in just_numbers:
							indices = [ir for ir, x in enumerate(just_numbers) if x == 14]
							ix = indices[0]
							print 'move ', draw_cards, ' to ', ix
							drag1(draw_cards,ix, sts, num_cards)
							num_cards[ix] = 1
							stack_cards[ix] = [card]
							remaining_draw_cards_tmp -= 1
							draw_cards_used += 1
							if draw_cards != 0:
								draw_cards -= 1
							moved = True
							all_false = False
							click = False
							print history,card
							history.remove(card)
						else:
							done = False
							for ix in range(6,-1,-1):
								card_ = stack_cards[ix][0]
								if card_[0] + 1 in just_numbers:
									indices = [ir for ir, x in enumerate(just_numbers) if x == card_[0] + 1]

									for ic in indices:
										if othercolor(card_[1],stack_cards[ic][-1][1]):
											drag(ix,ic, sts, num_cards)
											print 'move ', ix, ' to ', ic
											stack_cards[ic].extend(stack_cards[ix])
											#sts[ix]-=1 must stay 0
											num_cards[ic] += len(stack_cards[ix])
											num_cards[ix] = 1
											drag1(draw_cards,ix, sts, num_cards)
											print 'move ', draw_cards, ' to ', ix
											stack_cards[ix] = [card]
											remaining_draw_cards_tmp -= 1
											draw_cards_used += 1
											if draw_cards != 0:
												draw_cards -= 1
											moved = True
											all_false = False
											click = False
											done = True
											print history,card
											history.remove(card)
											break
								if done:
									break
									
						if all_false:
							click = True
				elif card[0] + 1 in just_numbers:
					indices = [ir for ir, x in enumerate(just_numbers) if x == card[0] + 1]
					all_false = True
					for ic in indices:
						if dontplay59 and not all([x<=0 for x in sts]):
							if card[0] >= 5 and card[0] <= 9:
								#will allow a play or transfer that will IMMEDIATELY free a downcard
								first_cards = [x[0] for x in stack_cards.values()]
								indices_of_plus_1 = [irs for irs, xx in enumerate(first_cards) if xx[0] == card[0] -1]
								for icc in indices_of_plus_1:
									if othercolor(card[1],stack_cards[icc][0][1]) and othercolor(card[1],stack_cards[ic][-1][1]) and sts[icc] > 0:
										print 'will free downcard ', stack_cards[ic][-1], card, stack_cards[icc][0]
										drag1(draw_cards,ic, sts, num_cards)
										stack_cards[ic].append(card)

										num_cards[ic] += 1
										remaining_draw_cards_tmp -= 1
										draw_cards_used += 1
										if draw_cards != 0:
											draw_cards -= 1
										moved = True
										all_false = False
										click = False
										history.remove(card)
										break
								if moved:
									break
								print 'after free downcard'
								#smooth with it's next highest even/odd partner in the column
								if num_cards[ic]>=2:
									if stack_cards[ic][-2][1] != card[1]:
										if no_moves == 1:
											if othercolor(card[1],stack_cards[ic][-1][1]):
												print 'no other moves possible'
												drag1(draw_cards,ic, sts, num_cards)
												stack_cards[ic].append(card)

												num_cards[ic] += 1
												remaining_draw_cards_tmp -= 1
												draw_cards_used += 1
												if draw_cards != 0:
													draw_cards -= 1
												moved = True
												all_false = False
												click = False
												no_moves -= 1
												history.remove(card)
												break
										else:
											continue
									else:
										if othercolor(card[1],stack_cards[ic][-1][1]):
											print 'smooth ', card, stack_cards[ic][-2]
											drag1(draw_cards,ic, sts, num_cards)
											stack_cards[ic].append(card)

											num_cards[ic] += 1
											remaining_draw_cards_tmp -= 1
											draw_cards_used += 1
											if draw_cards != 0:
												draw_cards -= 1
											moved = True
											all_false = False
											click = False
											history.remove(card)
											print 'breaking smooth'
											break
								else:
									#if there's only one card, it does not contravene against smoothness
									if othercolor(card[1],stack_cards[ic][-1][1]):
										print 'smooth ', card
										drag1(draw_cards,ic, sts, num_cards)
										stack_cards[ic].append(card)

										num_cards[ic] += 1
										remaining_draw_cards_tmp -= 1
										draw_cards_used += 1
										if draw_cards != 0:
											draw_cards -= 1
										moved = True
										all_false = False
										click = False
										history.remove(card)
										print 'breaking smooth'
										break
								# ABSOLUTELY no other choice to continue playing (this is not a good sign)
								print 'no_moves: ', no_moves
								if no_moves == 1:
									if othercolor(card[1],stack_cards[ic][-1][1]):
										print 'no other moves possible'
										drag1(draw_cards,ic, sts, num_cards)
										stack_cards[ic].append(card)

										num_cards[ic] += 1
										remaining_draw_cards_tmp -= 1
										draw_cards_used += 1
										if draw_cards != 0:
											draw_cards -= 1
										moved = True
										all_false = False
										click = False
										no_moves -= 1
										history.remove(card)
										break
							elif othercolor(card[1],stack_cards[ic][-1][1]):
								drag1(draw_cards,ic, sts, num_cards)
								stack_cards[ic].append(card)

								num_cards[ic] += 1
								remaining_draw_cards_tmp -= 1
								draw_cards_used += 1
								if draw_cards != 0:
									draw_cards -= 1
								moved = True
								all_false = False
								click = False
								print history,card
								history.remove(card)
								break
						else:
							if othercolor(card[1],stack_cards[ic][-1][1]):
								drag1(draw_cards,ic, sts, num_cards)
								stack_cards[ic].append(card)

								num_cards[ic] += 1
								remaining_draw_cards_tmp -= 1
								draw_cards_used += 1
								if draw_cards != 0:
									draw_cards -= 1
								moved = True
								all_false = False
								click = False
								print history,card
								history.remove(card)
								break
					if all_false:
						click = True
				else:
					click = True

				if not moved:
					if next_card_protected(aces,stack_cards,card) and [card[0] - 1,card[1]] in [x[-1] for x in aces.values()]:
						if draw_cards == 0:
							pyautogui.moveTo(918 - 18 * (3 - 1) + left + 10,154 + up + 10)
						else:
							pyautogui.moveTo(918 - 18 * (3 - draw_cards) + left + 10,154 + up + 10)
						pyautogui.click()
						time.sleep(0.1)
						pyautogui.click()

						#find color and add
						aces[[x[0] for x in aces.values()].index([1,card[1]])].append(card)
						remaining_draw_cards_tmp -= 1
						draw_cards_used += 1
						click = False
						moved = True
						if draw_cards != 0:
							draw_cards -= 1
						history.remove(card)
				if all([x<=0 for x in sts]):
					print 'should we stay in draw?'
					#raw_input()

				#print 'end of loop: ', math.floor((remaining_draw_cards-1)/3.0), triples, math.floor((remaining_draw_cards-1)/3.0) == triples
				#time.sleep(sleep_time)

				dra_card = card
				if math.floor((remaining_draw_cards-1)/div) == triples:
					s = 'moved: ', moved, ' not moved: ',not_moved, no_moves, remaining_draw_cards%3, 'draw_cards: ', draw_cards

					s = '#1: ', remaining_draw_cards,remaining_draw_cards_tmp, cards_seen, draw_cards, 'last triple'

					if not_moved:
						no_moves += 1
					if no_moves == stop_crit:
						i_end = 6
						end_moved_at_all = False
						print aces.values()
						print [x[-1] for x in aces.values()]
						#print stack_cards
						while i_end >= 0:

							#check for stack_cards again
							while all([x<=0 for x in sts]) and [dra_card[0] - 1,dra_card[1]] in [x[-1] for x in aces.values()]:
								if draw_cards == 0:
									pyautogui.moveTo(918 - 18 * (3 - 1) + left + 10,154 + up + 10)
								else:
									pyautogui.moveTo(918 - 18 * (3 - draw_cards) + left + 10,154 + up + 10)
								pyautogui.click()
								time.sleep(0.1)
								pyautogui.click()

								#find color and add
								aces[[x[0] for x in aces.values()].index([1,dra_card[1]])].append(dra_card)
								remaining_draw_cards_tmp -= 1
								draw_cards_used += 1
								click = False
								moved = True
								if draw_cards != 0:
									draw_cards -= 1
								history.remove(dra_card)

								if click or (triples == 0 and draw_cards == 0) or (cards_seen==draw_cards_used and cards_seen!=0):
									pyautogui.moveTo(810 + left, 180 + up)
									pyautogui.click()
									triples += 1
									#print 'in click: ', math.floor((remaining_draw_cards-1)/3.0), triples, math.floor((remaining_draw_cards-1)/3.0) > triples-1, remaining_draw_cards - (cards_seen)
									if math.floor((remaining_draw_cards-1)/div) > triples-1:
										if three_draw:
											if remaining_draw_cards - (cards_seen) >= 3:
												next_draw = 3
											else:
												next_draw = (remaining_draw_cards)%3 if (remaining_draw_cards)%3>0 else 3
										else:
											next_draw = 1
										cards_seen += next_draw
										draw_cards = next_draw
										s = '#3: ', remaining_draw_cards,remaining_draw_cards_tmp, cards_seen, next_draw, 'not last one'
										#print s
										#tex.insert(tk.END, s)
										#tex.see(tk.END)
										time.sleep(sleep_time_draw)
										
									elif math.floor((remaining_draw_cards-1)/div) == triples-1:
										time.sleep(0.32)
										pyautogui.moveTo(810 + left, 180 + up)
										pyautogui.click()
										rounds += 1
										triples = 0
										draw_cards_used = 0
										remaining_draw_cards = remaining_draw_cards_tmp
										if three_draw:
											draw_cards = 3 if remaining_draw_cards_tmp >= 3 else remaining_draw_cards_tmp
										else:
											draw_cards = 1
										cards_seen = draw_cards
										s = '#2: ', remaining_draw_cards_tmp, draw_cards, 'first one'
										#print s
										#tex.insert(tk.END, s)
										#tex.see(tk.END)
										not_moved = True
										time.sleep(sleep_time_draw)

								dra_card, _ = draw_card(clf_cards,clf_color,draw_cards, counter_draws)

							sorted_sts = [j[0] for j in sorted(enumerate(sts), key=lambda x:x[1])]
							i = sorted_sts[i_end]

							end_moved = False
							card = stack_cards[i][-1]
							print i, card, [card[0] - 1,card[1]] in [x[-1] for x in aces.values()]
							if  [card[0] - 1,card[1]] in [x[-1] for x in aces.values()]:
								print 'in if', card
								print sts, num_cards
								#raw_input()
								if sts[i] < 0:
									tmp = 0
								else:
									tmp = sts[i]
								pyautogui.moveTo((i*(card_width+stack_)) + 337 + left + 10,268 + 22 * (num_cards[i]-1) + 4*tmp + up + 10)
								pyautogui.click()
								time.sleep(0.1)
								pyautogui.click()
								time.sleep(0.4)

								#find color and add
								aces[[x[0] for x in aces.values()].index([1,card[1]])].append(card)
								#remove from stack
								del stack_cards[i][-1]
								num_cards[i] -= 1
								if num_cards[i] == 0:
									sts[i] -= 1
								
								end_moved = True
								if sts[i] >= 0 and num_cards[i] == 0:
									time.sleep(sleep_time_stack)
									im=ImageGrab.grab(bbox=((i*(card_width+stack_)) + 337 + left,268 + 4*sts[i] + up,(i*(card_width+stack_))+337 + card_width + left,4*sts[i] + 268 + card_height + up))
									img = im.convert('L')
									img = np.asarray(img)
									#im.convert('RGB').save("solitaire/debug/second2%s.jpg"%str(counter_second))
									stack_cards[i] = [[clf_cards.predict(img[2:,:-4].flatten().reshape(1, -1))[0], clf_color.predict(img[2:,:-4].flatten().reshape(1, -1))[0]]]
									np.savetxt("solitaire/debug/second2%s.txt"%str(counter_second), [stack_cards[i]], fmt='%s')
									num_cards[i] = 1
									counter_second += 1
								print 'in last: ', num_cards[i], stack_cards
								if num_cards[i] == 0:
									stack_cards[i] = [[14,'a']]
									#num_cards[i] = 0

							if end_moved:
								i_end = 6
								end_moved_at_all = True
							else:
								i_end -= 1
							print 'end_moved_at_all: ', end_moved_at_all
						if not end_moved_at_all:
							print 'stopping because two rouds not moved'
							#click stop
							#pyautogui.click(980 + left,75 + up)
							exit(-1)
						else:
							moved = True
							no_moves = 0
				if remaining_draw_cards_tmp == 0 and all([x<=0 for x in sts]):
					print 'won'
					exit(-1)
				if remaining_draw_cards_tmp == 0:
					print 'are we getting here in this case?'
			#print history
			if moved:
				not_moved = False

		exit(-1)
		
	except KeyboardInterrupt:
		exit(-1)
 	
if __name__ == '__main__':
	#top = tk.Tk()
	#tex = tk.Text(master=top)
	#tex.pack(side=tk.RIGHT)
	#bop = tk.Frame()
	#bop.pack(side=tk.LEFT)
	#top.configure(background='gold')
	#top.attributes("-topmost", True)
	#top.lift()
	#tex.insert(tk.END, '123456654334567654346789')
	#tex.see(tk.END)
	#raw_input()
	main()

#TODO:
# (-) what if there are no draw cards left
# (!) line 254, in main,     just_numbers = [x[-1][0] for x in stack_cards.values()] IndexError: list index out of range
# if two kings take the one that frees downcard
# but if king is there and can free downcard don't wait another round
# change order, we have do the last thing earlier in case it frees downcards
# before click check cards again
# two queens -> nothing even there were all kings
# if almost done (for example nly one card on draw, just open)
# if there's nothing to move first round on stacks it clicks on new draw
# one time it seemed to be stuck - while loop?
# if there's no card left in draw it seemed to be stuck in a loop
# sometimes it still clicks on the wrong card to put on foundation
# do we need to go through all draw_cards again after bringing cards to foundation?? did it make any difference?
# if we wait for next king we have to save space to free place for king... -> if king goes on 10 and ten on Jack, we cant put other 10 on Jack
# (?) sleep time shroter, just if 2d check again!
# (?) if there's a 4 red on board, don't put 3 black on foundation if not protected, if it's better to put it on other stack
# two black quuens and red king drawn and empty field but not playing king!
# (/) if all(sts<1), play draw cards first -> faster
# sometimes we can't put all cards on foundation because then draw cards can't go on stacks anymore (next protected), so when we do that we have to have an eye on drawcards


# (?) = maybe fixed
# (-) = probably fixed
# (/) = probably still not fixed
# (!) = fixed


#why does it not play 4c (numcards==1, sts>0) if 3c is in aces
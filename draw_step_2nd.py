import numpy as np
from copy import deepcopy

def sort_cards(cards):
    #put ace at end
    return sorted(cards)[::-1]


def value(cards):
    cards = sort_cards(cards)
    #for now ace is only 11
    ret = 0
    for c in cards:
        if c == 14:
            ret = 21
        elif c == 1:
            if ret>10:
                ret += 1
            else:
                ret += 11
        elif c>=10:
            ret += 10
        else:
            ret += c
    return ret


def bj(cards):
    v = value(cards)
    if v==21:
        return True
    else:
        return False


class State(object):
    def __init__(self, card, points, history, field_0, field_1, field_2, field_3):
        self.points = points
        self.card = card
        self.remaining = [1,1,1,1,2,2,2,2,3,3,3,3,4,4,4,4,5,5,5,5,6,6,6,6,7,7,7,7,8,8,8,8,9,9,9,9,10,10,10,10,11,11,12,12,12,12,13,13,13,13,14,14]
        #self.history = history
        self.field_0 = field_0
        self.field_1 = field_1
        self.field_2 = field_2
        self.field_3 = field_3
        if self.card[0].isdigit() and self.card[1].isdigit():
            if self.card == '11c' or self.card == '11s':
                self.value_card = 14
            else:
                self.value_card = int(self.card[0:2])
        else:
            self.value_card = int(self.card[0])

    def allowed(self):
        tmp = [value(self.field_0 + [self.value_card]), value(self.field_1 + [self.value_card]),value(self.field_2 + [self.value_card]),value(self.field_3 + [self.value_card])]
        return np.concatenate([np.argwhere(np.array(tmp)<22).flatten(),[4]])

    def get_signature(self):
        #return val of 4 fields
        return [self.field_0,self.field_1,self.field_2,self.field_3]

    def copy(self):
        return State(self.card, self.points, None, self.field_0, self.field_1, self.field_2, self.field_3)

    def draw(self, card):
        self.card = card
        if self.card[0].isdigit() and self.card[1].isdigit():
            if self.card == '11c' or self.card == '11s':
                self.value_card = 14
            else:
                self.value_card = int(self.card[0:2])
        else:
            self.value_card = int(self.card[0])

    def print_(self):
        print 'card: ', self.card,' fields: ', self.field_0, self.field_1, self.field_2, self.field_3, ' points: ', self.points

    def update_state(self, action):
        #TODO: add history to know how many remaining cards with this value

        self.remaining.remove(self.value_card)
        a_card = self.card
        if action == 0:
            self.field_0.append(self.value_card)
            if len(self.field_0) == 5:
                if value(self.field_0)>21:
                    print 'error too much value, burst 0', self.field_0, value(self.field_0), value(self.field_0)>21
                    exit(-1)
                self.points += 100
                self.field_0 = []
            elif a_card == '11c' or a_card == '11s':
                self.points += 75
                self.field_0 = []

            elif bj(self.field_0):
                self.points += 50
                self.field_0 = []
        if action == 1:
            self.field_1.append(self.value_card)
            if len(self.field_1) == 5:
                if value(self.field_1)>21:
                    print 'error too much value, burst 1', self.field_1, value(self.field_1), value(self.field_1)>21
                    exit(-1)
                self.points += 100
                self.field_1 = []
            elif a_card == '11c' or a_card == '11s':
                self.points += 75
                self.field_1 = []

            elif bj(self.field_1):
                self.points += 50
                self.field_1 = []
        if action == 2:
            self.field_2.append(self.value_card)
            if len(self.field_2) == 5:
                if value(self.field_2)>21:
                    print 'error too much value, burst 2', self.field_2, value(self.field_2),value(self.field_2)>21
                    exit(-1)
                self.points += 100
                self.field_2 = []
            elif a_card == '11c' or a_card == '11s':
                self.points += 75
                self.field_2 = []

            elif bj(self.field_2):
                self.points += 50
                self.field_2 = []
        if action == 3:
            self.field_3.append(self.value_card)
            if len(self.field_3) == 5:
                if value(self.field_3)>21:
                    print 'error too much value, burst 3', self.field_3, value(self.field_3),value(self.field_3)>21
                    exit(-1)
                self.points += 100
                self.field_3 = []
            elif a_card == '11c' or a_card == '11s':
                self.points += 75
                self.field_3 = []

            elif bj(self.field_3):
                self.points += 50
                self.field_3 = []
        if action == 4:
            self.points -= 5

def step(state, action, a_card):

    state_ret = state.copy()
    state_ret.update_state(action)
    state_ret.draw(a_card)
    return state_ret


def get_reward_from_state(state):
    ret = state.points
    return ret



if __name__ == '__main__':
    check_draw('checkDraw.csv', 1000)
    check_step(1000)
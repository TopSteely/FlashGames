import numpy as np
from copy import deepcopy

def sort_cards(cards):
    #put ace at end
    temp = []
    aces = []
    for i_c,c in enumerate(cards):
        if int(c[0])==1 and c[1].isalpha():
            aces.append(c)
        else:
            temp.append(c)
    temp.extend(aces)
    return temp


def value(cards):
    cards = sort_cards(cards)
    #for now ace is only 11
    ret = [0]
    for c in cards:
        if c == '11c' or c == '11s':
            ret[0] = 21
        elif int(c[0])==1 and c[1].isalpha():
            if ret[0]>10:
                ret[0] += 1
            else:
                ret[0] += 11
        elif int(c[0])==1 and c[1].isdigit():
            ret[0] += 10
        else:
            ret[0] += int(c[0])
    return ret


def bj(cards):
    v = value(cards)
    if v[0]==21 or (len(v)>1 and v[1]==21):
        return True
    else:
        return False


class State(object):
    def __init__(self, card, points, history, field_0, field_1, field_2, field_3):
        self.points = points
        self.card = card
        #self.history = history
        self.field_0 = field_0
        self.field_1 = field_1
        self.field_2 = field_2
        self.field_3 = field_3

    def allowed(self):
        tmp = [value(self.field_0 + [self.card]), value(self.field_1 + [self.card]),value(self.field_2 + [self.card]),value(self.field_3 + [self.card])]
        #print 'in allowed: ', tmp, np.concatenate([np.argwhere(np.array([t[0] for t in tmp])<22).flatten(),[4]])
        return np.concatenate([np.argwhere(np.array([t[0] for t in tmp])<22).flatten(),[4]])

    def get_signature(self):
        #return val of 4 fields
        c = self.card
        if c == '11c' or c == '11s':
            s = 12
        elif int(c[0])==1 and c[1].isalpha():
            s = 11
        elif int(c[0])==1 and c[1].isdigit():
            s = 10
        else:
            s = int(c[0])
        return [s,value(self.field_0)[0],value(self.field_1)[0],value(self.field_2)[0],value(self.field_3)[0]]

    def copy(self):
        return State(self.card, self.points, None, self.field_0, self.field_1, self.field_2, self.field_3)

    def draw(self, card):
        self.card = card

    def print_(self):
        print 'card: ', self.card,' fields: ', self.field_0, self.field_1, self.field_2, self.field_3, ' points: ', self.points

    def update_state(self, action):
        #TODO: add history to know how many remaining cards with this value
        a_card = self.card
        if action == 0:
            self.field_0.append(a_card)
            if len(self.field_0) == 5:
                if value(self.field_0)[0]>21:
                    print 'error too much value, burst 0', self.field_0, value(self.field_0)[0], value(self.field_0)[0]>21
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
            self.field_1.append(a_card)
            if len(self.field_1) == 5:
                if value(self.field_1)[0]>21:
                    print 'error too much value, burst 1', self.field_1, value(self.field_1)[0], value(self.field_1)[0]>21
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
            self.field_2.append(a_card)
            if len(self.field_2) == 5:
                if value(self.field_2)[0]>21:
                    print 'error too much value, burst 2', self.field_2, value(self.field_2)[0],value(self.field_2)[0]>21
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
            self.field_3.append(a_card)
            if len(self.field_3) == 5:
                if value(self.field_3)[0]>21:
                    print 'error too much value, burst 3', self.field_3, value(self.field_3)[0],value(self.field_3)[0]>21
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
from draw_step import *
from Catch21 import get_labels
import numpy as np
import random
import pickle


class StateAction(object):
    """
    The implementation of (state, action) => value
    For Q function, eligibility trace and counts
    """
    def __init__(self):
        #self.buffer = np.zeros([13, 21, 21, 21, 21, 5])
        # change to dict of remaining, card, state0, state1, state2, state3, action
        # 14 = black jacks
        self.buffer = {}
        #self.remaining = [1,1,1,1,2,2,2,2,3,3,3,3,4,4,4,4,5,5,5,5,6,6,6,6,7,7,7,7,8,8,8,8,9,9,9,9,10,10,10,10,11,11,12,12,12,12,13,13,13,13,14,14]
        #self.state0 = []
        #self.state1 = []
        #self.state2 = []
        #self.state3 = []

    # get value of a given state-action pair
    def get_value(self, remaining, card, state, action):
    	if remaining in self.buffer:
    		if card in self.buffer[remaining]:
    			if state[0] in self.buffer[remaining][card]:
    				if state[1] in self.buffer[remaining][card][state[0]]:
    					if state[2] in self.buffer[remaining][card][state[0]][state[1]]:
    						if state[3] in self.buffer[remaining][card][state[0]][state[1]][state[2]]:
    							if action in self.buffer[remaining][card][state[0]][state[1]][state[2]][state[3]]:
    								return self.buffer[remaining][card][state[0]][state[1]][state[2]][state[3]][action]
    	else:
    		return 0

    # increment the value by inc
    def inc_value(self, remaining, card, state, action, inc):
        if remaining in self.buffer:
    		if card in self.buffer[remaining]:
    			if state[0] in self.buffer[remaining][card]:
    				if state[1] in self.buffer[remaining][card][state[0]]:
    					if state[2] in self.buffer[remaining][card][state[0]][state[1]]:
    						if state[3] in self.buffer[remaining][card][state[0]][state[1]][state[2]]:
    							if action in self.buffer[remaining][card][state[0]][state[1]][state[2]][state[3]]:
    								self.buffer[remaining][card][state[0]][state[1]][state[2]][state[3]][action] += inc
    							else:
    								self.buffer[remaining][card][state[0]][state[1]][state[2]][state[3]][action] = inc
    						else:
    							self.buffer[remaining][card][state[0]][state[1]][state[2]][state[3]] = []
    							self.buffer[remaining][card][state[0]][state[1]][state[2]][state[3]][action] = inc
    					else:
    						self.buffer[remaining][card][state[0]][state[1]][state[2]] = []
    						self.buffer[remaining][card][state[0]][state[1]][state[2]][state[3]] = []
    						self.buffer[remaining][card][state[0]][state[1]][state[2]][state[3]][action] = inc
    				else:
    					self.buffer[remaining][card][state[0]][state[1]] = []
    					self.buffer[remaining][card][state[0]][state[1]][state[2]] = []
						self.buffer[remaining][card][state[0]][state[1]][state[2]][state[3]] = []
						self.buffer[remaining][card][state[0]][state[1]][state[2]][state[3]][action] = inc
				else:
					self.buffer[remaining][card][state[0]] = []
					self.buffer[remaining][card][state[0]][state[1]] = []
					self.buffer[remaining][card][state[0]][state[1]][state[2]] = []
					self.buffer[remaining][card][state[0]][state[1]][state[2]][state[3]] = []
					self.buffer[remaining][card][state[0]][state[1]][state[2]][state[3]][action] = inc
			else:
				self.buffer[remaining][card] = []
				self.buffer[remaining][card][state[0]] = []
				self.buffer[remaining][card][state[0]][state[1]] = []
				self.buffer[remaining][card][state[0]][state[1]][state[2]] = []
				self.buffer[remaining][card][state[0]][state[1]][state[2]][state[3]] = []
				self.buffer[remaining][card][state[0]][state[1]][state[2]][state[3]][action] = inc
    	else:
    		self.buffer[remaining] = []
    		self.buffer[remaining][card] = []
			self.buffer[remaining][card][state[0]] = []
			self.buffer[remaining][card][state[0]][state[1]] = []
			self.buffer[remaining][card][state[0]][state[1]][state[2]] = []
			self.buffer[remaining][card][state[0]][state[1]][state[2]][state[3]] = []
			self.buffer[remaining][card][state[0]][state[1]][state[2]][state[3]][action] = inc

    # set the value to be val
    def set_value(self, remaining, card, state, action, val):
        if remaining in self.buffer:
    		if card in self.buffer[remaining]:
    			if state[0] in self.buffer[remaining][card]:
    				if state[1] in self.buffer[remaining][card][state[0]]:
    					if state[2] in self.buffer[remaining][card][state[0]][state[1]]:
    						if state[3] in self.buffer[remaining][card][state[0]][state[1]][state[2]]:
    							self.buffer[remaining][card][state[0]][state[1]][state[2]][state[3]][action] = val
    						else:
    							self.buffer[remaining][card][state[0]][state[1]][state[2]][state[3]] = []
    							self.buffer[remaining][card][state[0]][state[1]][state[2]][state[3]][action] = val
    					else:
    						self.buffer[remaining][card][state[0]][state[1]][state[2]] = []
    						self.buffer[remaining][card][state[0]][state[1]][state[2]][state[3]] = []
    						self.buffer[remaining][card][state[0]][state[1]][state[2]][state[3]][action] = val
    				else:
    					self.buffer[remaining][card][state[0]][state[1]] = []
    					self.buffer[remaining][card][state[0]][state[1]][state[2]] = []
						self.buffer[remaining][card][state[0]][state[1]][state[2]][state[3]] = []
						self.buffer[remaining][card][state[0]][state[1]][state[2]][state[3]][action] = val
				else:
					self.buffer[remaining][card][state[0]] = []
					self.buffer[remaining][card][state[0]][state[1]] = []
					self.buffer[remaining][card][state[0]][state[1]][state[2]] = []
					self.buffer[remaining][card][state[0]][state[1]][state[2]][state[3]] = []
					self.buffer[remaining][card][state[0]][state[1]][state[2]][state[3]][action] = val
			else:
				self.buffer[remaining][card] = []
				self.buffer[remaining][card][state[0]] = []
				self.buffer[remaining][card][state[0]][state[1]] = []
				self.buffer[remaining][card][state[0]][state[1]][state[2]] = []
				self.buffer[remaining][card][state[0]][state[1]][state[2]][state[3]] = []
				self.buffer[remaining][card][state[0]][state[1]][state[2]][state[3]][action] = val
    	else:
    		self.buffer[remaining] = []
    		self.buffer[remaining][card] = []
			self.buffer[remaining][card][state[0]] = []
			self.buffer[remaining][card][state[0]][state[1]] = []
			self.buffer[remaining][card][state[0]][state[1]][state[2]] = []
			self.buffer[remaining][card][state[0]][state[1]][state[2]][state[3]] = []
			self.buffer[remaining][card][state[0]][state[1]][state[2]][state[3]][action] = val

    def reset(self):
        self.buffer = {}

    def save_buffer(self, path):
        #np.save(path, self.buffer)
        pickle.dump(self.buffer, open(path, 'wb'))

    def load_from_buffer(self, path):
        #self.buffer = np.load(path)
        with open(path, 'rb') as handle:
    		self.buffer = pickle.load(handle)

    def check_q(self, path):
        rows = []
        for c in range(13):
	        for field_0 in range(21):
	        	for field_1 in range(21):
	        		for field_2 in range(21):
	        			for field_3 in range(21):
	        				for action in range(5):
	        					rows.append((c + 1,field_0 + 1,field_1 + 1,field_2 + 1,field_3 + 1, player_sum + 1, action, self.buffer[c,field_0,field_1,field_2,field_3, player_sum, action]))
        mat = np.asarray(rows)
        np.savetxt(path, mat, delimiter=',')


class QFunction(StateAction):
    # get the action with maximum value given a state
    def get_action(self, remaining, card, state, verbose):
        state_sig = state.get_signature()
        allowed = state.allowed()
        values = []
        for action in allowed:
        	values.append(self.getValue(remaining, card, state, action))
        #ac = allowed[np.argmax(self.buffer[state_sig[0] - 1, state_sig[1] - 1,state_sig[2] - 1,state_sig[3] - 1, state_sig[4] - 1, allowed])]
        ac = allowed[np.argmax(values)]
        if verbose:
    		print 'state: ', state_sig, state.print_()
    		print 'buffer: ', self.buffer[state_sig[0] - 1, state_sig[1] - 1,state_sig[2] - 1,state_sig[3] - 1, state_sig[4] - 1, allowed]
    		print 'action: ', ac
        return ac

    def get_Q(self):
        return self.buffer

    def get_V(self):
        return np.max(self.buffer, axis=4)

    def inc_batch(self, state_action, mul):
        self.buffer += state_action.buffer * mul

    def mse(self, Q):
        return np.mean((self.buffer - Q.buffer) ** 2)


def one_episode(policy):
    cards = get_labels()
    random.shuffle(cards)
    state = State(cards[0], 0, None, [], [], [], [])

    policy.start_new_episode()
    for i_c,c in enumerate(cards[1:]):
        action = policy.next_action(state)
        state_new = step(state, action, c)
        #reward = get_reward_from_state(state_new)
        #policy.update_policy_online(state, state_new, action, reward)
        state = state_new
    reward = get_reward_from_state(state_new)
    policy.update_policy_online(state, state_new, action, reward)
    return get_reward_from_state(state_new)


def sample_indices(prob_mat):
    probs = np.reshape(prob_mat, prob_mat.size)
    location = np.random.choice(np.arange(prob_mat.size), size=1, p=probs)[0]
    row = location / 21
    column = location % 21
    return row, column


class StateTransition(object):
    """
    modeling state transition
    """
    def __init__(self):
        # conditional transition probability to non-terminal state
        self.buffer = np.ones((13, 21, 21, 21, 21), dtype=np.float64) / 21.0
        # transition to terminal state
        self.to_terminal = StateAction()
        self.to_terminal.buffer[:, :, :, :, :, 0] = 0.2
        self.to_terminal.buffer[:, :, :, :, :, 1] = 0.2
        self.to_terminal.buffer[:, :, :, :, :, 2] = 0.2
        self.to_terminal.buffer[:, :, :, :, :, 3] = 0.2
        self.to_terminal.buffer[:, :, :, :, :, 4] = 0.2
        # state-action count
        # self.count = StateAction()
        # self.count.buffer += 1
        self.player_sum_count = np.ones(21)

    def get_next_state(self, state, action):
        prob_terminal = self.to_terminal.get_value(state, action)
        next_terminal = np.random.choice((False, True), size=1, p=(1.0 - prob_terminal, prob_terminal))[0]
        if next_terminal:
            next_state = state.copy()
            next_state.set_terminal()
            if action == 0:
                next_state.player_sum = -1
            return next_state
        else:
            state_sig = state.get_signature()
            prob = self.buffer[state_sig[1] - 1, :]
            next_player_sum = np.random.choice(np.arange(1, 22), size=1, p=prob)[0]
            return State(state_sig[0], next_player_sum, False)

    def update_model(self, state, action, new_state):
        # t = self.count.get_value(state, action)
        state_sig = state.get_signature()
        t = self.player_sum_count[state_sig[1] - 1]
        if new_state.is_terminal:
            # update terminal probability
            old_prob = self.to_terminal.get_value(state, action)
            new_prob = (old_prob * t + 1.0) / (t + 1.0)
            self.to_terminal.set_value(state, action, new_prob)
        else:
            # update conditional probability
            new_state_sig = new_state.get_signature()
            term_prob = self.to_terminal.get_value(state, action)
            old_prob = self.buffer[state_sig[1] - 1, new_state_sig[1] - 1]
            new_prob = (old_prob * (1.0 - term_prob) * t + 1) / ((1.0 - term_prob) * t + 1.0)
            self.buffer[state_sig[1] - 1, new_state_sig[1] - 1] = new_prob
            self.buffer[state_sig[1] - 1, :] *= 1 / self.buffer[state_sig[1] - 1, :].sum()
            # update terminal probability
            new_term_prob = (term_prob * t) / (t + 1.0)
            self.to_terminal.set_value(state, action, new_term_prob)
        # self.count.inc_value(state, action, 1)
        self.player_sum_count[state_sig[1] - 1] += 1
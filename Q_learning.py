from utils import *
from collections import Counter
import pickle


class Q_Learning_Control(object):
    def __init__(self):
        self.Q = QFunction()
        self.state_action_count = StateAction()
        self.in_use = False

    def set_in_use(self, is_in_use):
        self.in_use = is_in_use

    def start_new_episode(self):
        pass

    def next_action(self, state):
        """
        Behaviour policy: compeletely random
        Learnt policy: greedy wrt. Q
        :return: an action
        """
        if self.in_use:
            proposed_action = self.Q.get_action(state, True)
            print 'state: ', state.get_signature(), ' action: ', proposed_action
        else:
            #proposed_action = np.random.choice((0, 1), size=1, p=(0.5, 0.5))[0]
            #5 options, check if allowed and return random
            allowed = state.allowed()
            proposed_action = np.random.choice(allowed, size=1)
            self.state_action_count.inc_value(state, proposed_action, 1.0)
        return proposed_action

    def update_policy_online(self, state, state_new, action, reward):
        if self.in_use:
            pass
        else:
            q_old = self.Q.get_value(state, action)
            sa_n = self.state_action_count.get_value(state, action)
            alternative_action = self.Q.get_action(state_new, False)
            alternative_q = self.Q.get_value(state_new, alternative_action)
            self.Q.inc_value(state, action, (reward + alternative_q - q_old) / sa_n)

    def update_policy_batch(self, state, state_new, action, reward):
        pass


def Q_Learning_simulation(learning_episode, evaluation_episode):
    policy = Q_Learning_Control()
    for i in xrange(learning_episode):
        one_episode(policy)
    policy.Q.save_buffer('Q_Learning_Q')
    policy.set_in_use(True)
    result = [one_episode(policy) for i in xrange(evaluation_episode)]
    print Counter(result)
    #with open() as handle:
    #    pickle.save()

if __name__ == '__main__':
    Q_Learning_simulation(40000, 100)


#TODO:
# history or remaining cards
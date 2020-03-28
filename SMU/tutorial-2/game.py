import gym
from gym import spaces
from gym.utils import seeding

'''
This file is based on:
https://github.com/openai/gym/blob/master/gym/envs/toy_text/roulette.py
The modification is done so that some common mistakes in implementation
are more likely to arise.
'''

INIT_MAX = 10
MAX_ALLOWED_TOKENS = 20


class RouletteEnv(gym.Env):
    """Simple roulette environment

    The roulette wheel has 37 spots. If the bet is 0 and a 0 comes up,
    you win a reward of 35. If the parity of your bet matches the parity
    of the spin, you win 1. Otherwise, you lose -1.

    The long run reward for playing 0 should be -1/37 for any state
    The last action (37) stops the rollout for a return of your reward so far.

    You start with a random number of tokens which you bet. Initially, it is between
    one and 10. In each turn, you bet one token.

    The observation contains two parts: first is your cumulative reward so
    far, the second is the last number that has fallen on the roulette.

    Action 37 means that you want to cash your reward and walk away. The
    casino does not allow you to play on loan. Also if you own more than
    50 tokens, the security expells you from the casino.
    """
    def __init__(self, spots=37):
        self.n = spots + 1
        self.action_space = spaces.Discrete(self.n)
        self.observation_space = spaces.Discrete(1)
        self.seed()
        self.tokens:int = 0

    def seed(self, seed=None):
        self.np_random, seed = seeding.np_random(seed)
        return [seed]

    def step(self, action):
        assert self.action_space.contains(action)

        if action == self.n - 1:
            # observation, reward, done, info
            return (self.tokens, self.get_val()), self.tokens, True, {}

        # N.B. np.random.randint draws from [A, B) while random.randint draws from [A,B]
        val = self.get_val()
        if val == action == 0:
            self.tokens += self.n - 2
        elif val != 0 and action != 0 and val % 2 == action % 2:
            self.tokens += 1
        else:
            self.tokens += -1

        if self.tokens > MAX_ALLOWED_TOKENS or self.tokens < 1:
            return (self.tokens, val), self.tokens, True, {}

        return (self.tokens, val), 0, False, {}

    def reset(self):
        self.tokens = self.np_random.randint(1, INIT_MAX)
        return (self.tokens, self.get_val())

    def render(self, mode='human', close=False):
        """
        Prints the situation to the terminal. Call env.render() any time
        you need to see the game. This method is useful for debugging.
        """
        print("You own " + str(self.tokens) + " tokens.")

    def get_val(self):
        return self.np_random.randint(0, self.n - 1)


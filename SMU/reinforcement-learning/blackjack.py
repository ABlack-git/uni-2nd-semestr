from builtins import str, bool
from enum import Enum

import gym
from gym import spaces
from gym import Space
from gym.utils import seeding
from carddeck import *
import copy


class BlackjackObservation(Space):
    """
    Observation that is given to you after each step
    you are not allowed to write to this object
    """

    def __init__(self, player_hand: BlackjackHand, dealer_hand: BlackjackHand):
        self.player_hand = player_hand
        self.dealer_hand = dealer_hand

    def __repr__(self):
        return "Blackjack(player: " + str(self.player_hand) + ", dealer: " + str(self.dealer_hand) + ")"


class BlackjackEnv(gym.Env):
    """
    our implementation of environment for blackjack game env.
    check superclass implementation in
    https://github.com/openai/gym/blob/master/gym/core.py

    you are not allowed to write to instances of this object
    or read values that you should not (for example what is
    the next card that will be drawn)

    However, the variables are still visible to your code for
    purposes of evaluation and testing.
    """

    metadata = {'render.modes': ['human']}

    def __init__(self):
        self.action_space = spaces.Discrete(2)
        self.seed()
        self.reset()
        self._owns_render = False

    def step(self, action: int):
        """
        Does one step. At the end of the game you are responsible yourself
        for calling env.reset().

        For more details visit:
        https://github.com/openai/gym/blob/master/gym/core.py

        :param action: Accepts action 1 (draw a card) or 0 (stick and let dealer move)

        :returns: tuple (observation, reward, done, info)
            WHERE
            BlackjackObservation observation is an instance of BlackjackObservation
            float reward is the reward (1.0 for win, -1.0 for loose, 0.0 throughout the game or for a tie)
            bool done is True when reaching terminal state
            dict info is empty dictionary, ignore in this setting
        """
        assert self.action_space.contains(action)

        if action == 1:
            self.player_hand.draw_card(self.deck)
            if self.player_hand.is_bust():
                return self._get_observation(), -1, True, {}
            else:
                return self._get_observation(), 0, False, {}
        else:
            # now play the dealer
            while self.dealer_hand.value() < 17:
                self.dealer_hand.draw_card(self.deck)
            player_value = self.player_hand.value()
            dealer_value = self.dealer_hand.value()
            if player_value > dealer_value or self.dealer_hand.is_bust():
                return self._get_observation(), 1, True, {}
            if player_value < dealer_value:
                return self._get_observation(), -1, True, {}
            return self._get_observation(), 0, True, {}

    def reset(self) -> BlackjackObservation:
        """
        Starts a new game. A new card deck is created, it is shuffled,
        player gets two cards and dealer has one visible.

        :returns: This method returns observation in BlackjackObservation object.
        :rtype: BlackjackObservation
        """
        self.deck = CardDeck()
        self.deck.shuffle(self.np_random)
        # print(self.deck.cards)
        self.player_hand = BlackjackHand()
        self.dealer_hand = BlackjackHand()
        self.player_hand.draw_card(self.deck)
        self.player_hand.draw_card(self.deck)
        self.dealer_hand.draw_card(self.deck)  # drawing 1 isđ equivalent to have 1 hidden
        # self._render()
        return self._get_observation()

    def render(self, mode: str = 'human', close: bool = False):
        """
        Prints the situation to the terminal. Call env.render() any time
        you need to see the game. This method is useful for debugging.
        """
        print("player: " + str(self.player_hand))
        print("dealer: " + str(self.dealer_hand))

    def _get_observation(self):
        return BlackjackObservation(copy.deepcopy(self.player_hand), copy.deepcopy(self.dealer_hand))

    def seed(self, seed: int = None):
        self.np_random, seed = seeding.np_random(seed)
        return [seed]


class BlackjackAction(Enum):
    """
    Enum for actions of the agent. Agent can either stand or hit.
    """
    # Take another card from the dealer
    HIT = 1
    # Stop playing
    STAND = 0

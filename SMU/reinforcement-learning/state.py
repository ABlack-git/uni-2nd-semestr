import numpy as np
import os
from typing import Tuple
from blackjack import BlackjackObservation, BlackjackAction
from carddeck import BlackjackHand, Rank
from typing import Union


class StateIndex:
    BUSTED = 0
    DEALER_PLAYED = 1
    GAME_ON = 2

    def __init__(self, state_type: int, state_index: Tuple):
        self.type = state_type
        self.index = state_index


class StateMap:
    """
    This class appeared due to confusion between AIMA book and Sutton. Ideally we do not need to store terminal states,
    as their q and count == 0, when using Sutton pseudo code.
    """
    def __init__(self, busted: Union[int, np.ndarray], dealer_played: np.ndarray, game_on: np.ndarray):
        self.busted_type = type(busted)
        self.array = {
            StateIndex.BUSTED: busted,
            StateIndex.DEALER_PLAYED: dealer_played,
            StateIndex.GAME_ON: game_on
        }

    def __getitem__(self, item: Union[StateIndex, Tuple[int, slice]]):
        if isinstance(item, tuple):
            return self.array[item[0]][item[1]]

        if item.type == StateIndex.BUSTED and self.busted_type is not np.ndarray:
            return self.array[item.type]
        return self.array[item.type][item.index]

    def __setitem__(self, key: StateIndex, value):
        if key.type == StateIndex.BUSTED and self.busted_type is not np.ndarray:
            self.array[key.type] = value
        else:
            self.array[key.type][key.index] = value

    def save(self, path, group):
        folder = os.path.join(path, group)
        if not os.path.exists(folder):
            os.makedirs(folder)
        np.save(os.path.join(folder, 'file_0'), self.array[StateIndex.BUSTED])
        np.save(os.path.join(folder, 'file_1'), self.array[StateIndex.DEALER_PLAYED])
        np.save(os.path.join(folder, 'file_2'), self.array[StateIndex.GAME_ON])

    @staticmethod
    def load(path, group):
        busted = np.load(os.path.join(path, group, 'file_0.npy'))
        dealer_played = np.load(os.path.join(path, group, 'file_1.npy'))
        game_on = np.load(os.path.join(path, group, 'file_2.npy'))
        if busted.size == 1:
            busted = int(busted)
        return StateMap(busted, dealer_played, game_on)


class State:
    PLAYER_NUM_STATES = 18
    DEALER_NUM_STATES = 19
    DEALER_ONE_CARD_NUM_STATES = 10
    HAS_ACE_NUM_STATES = 2
    __TWO_CARDS_LOW = 4
    __ONE_CARD_LOW = 2

    def __init__(self, player_sum, dealer_played, dealer_sum, has_active_ace):
        self.player_sum = player_sum if player_sum <= 21 else -1
        self.dealer_sum = dealer_sum if dealer_sum <= 21 else -1
        self.has_active_ace = has_active_ace
        self.dealer_played = dealer_played

    def state_index(self) -> StateIndex:
        # terminal states
        if self.player_sum == -1:
            return StateIndex(StateIndex.BUSTED, None)
        if self.dealer_played:
            player_idx = self.player_sum - State.__TWO_CARDS_LOW
            dealer_idx = State.DEALER_NUM_STATES - 1 if self.dealer_sum == -1 else \
                self.dealer_sum - State.__TWO_CARDS_LOW
            return StateIndex(StateIndex.DEALER_PLAYED, (player_idx, dealer_idx))
        # casual states
        player_idx = self.player_sum - State.__TWO_CARDS_LOW
        dealer_idx = self.dealer_sum - State.__ONE_CARD_LOW
        return StateIndex(StateIndex.GAME_ON, (player_idx, dealer_idx, int(self.has_active_ace)))

    def state_index_with_action(self, action: int) -> StateIndex:
        state_idx = self.state_index()
        if state_idx.index is None:
            state_idx.index = action
        else:
            state_idx.index = (*state_idx.index, action)
        return state_idx

    @staticmethod
    def obs_to_state(observation: BlackjackObservation):
        has_active_ace = hand_has_active_ace(observation.player_hand)
        dealer_played = False
        if len(observation.dealer_hand.cards) > 1:
            dealer_played = True
        return State(observation.player_hand.value(), dealer_played, observation.dealer_hand.value(), has_active_ace)


def hand_has_active_ace(hand: BlackjackHand) -> bool:
    has_ace = False
    value = 0
    for card in hand.cards:
        if card.rank is Rank.ACE:
            has_ace = True
        value += card.value()
    return has_ace and value + 10 <= 21

import utils
from typing import Tuple
from blackjack import BlackjackObservation, BlackjackAction


class State:
    PLAYER_NUM_STATES = 19
    DEALER_NUM_STATES = 10
    HAS_ACE_NUM_STATES = 2
    __PLAYER_SUM_LOW = 4
    __DEALER_SUM_LOW = 1

    def __init__(self, player_sum, dealer_sum, has_active_ace):
        self.player_sum = player_sum if player_sum <= 21 else -1
        self.dealer_sum = dealer_sum
        self.has_active_ace = has_active_ace

    def state_index(self) -> Tuple[int, int, int]:
        if self.player_sum == -1:
            player_idx = State.PLAYER_NUM_STATES - 1
        else:
            player_idx = self.player_sum - State.__PLAYER_SUM_LOW

        has_ace_idx = int(self.has_active_ace)
        dealer_idx = self.dealer_sum - State.__DEALER_SUM_LOW
        return player_idx, dealer_idx, has_ace_idx

    def state_index_with_action(self, action: BlackjackAction):
        state_idx = self.state_index()
        return *state_idx, action.value()

    @staticmethod
    def obs_to_state(observation: BlackjackObservation):
        has_active_ace = utils.hand_has_active_ace(observation.player_hand)
        return State(observation.player_hand.value(), observation.dealer_hand.cards[0].value(), has_active_ace)

from typing import Iterable, Tuple

from src.game import Rule
from src.utils import strToValue, DELIMITER


class HighCard(Rule):
    def __init__(self):
        pass

    def value(self, card: str) -> int:
        return strToValue[card.split(DELIMITER)[0]]

    def whoWins(self, hands: Tuple[Iterable[str], Iterable[str]]) -> int:
        max_hand1 = max([self.value(card) for card in hands[0]])
        max_hand2 = max([self.value(card) for card in hands[1]])
        return 0 if max_hand1 >= max_hand2 else 1


class AtLeastOnePair(Rule):
    def __init__(self):
        pass

    def value(self, card: str) -> int:
        return strToValue[card.split(DELIMITER)[0]]

    def whoWins(self, hands: Tuple[Iterable[str], Iterable[str]]) -> int:
        hand_0_wins = False
        for i, c1 in enumerate(hands[0]):
            for j, c2 in enumerate(hands[0]):
                if j <= i:
                    continue
                if self.value(c1) == self.value(c2):
                    hand_0_wins = True
        return 0 if hand_0_wins else 1

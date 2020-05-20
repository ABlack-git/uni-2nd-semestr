import random
from typing import Tuple, Iterable, List

from src.utils import valueToNumber, strToValue, DELIMITER

'''
This file contains main classes for the assignment.
'''


class Rule:
    '''
    General interface with only one method which says whether which player wins.
    '''

    def whoWins(self, hands: Tuple[Iterable[str], Iterable[str]]) -> int:
        '''
        Returns 0 if the first hand winds, 1 otherwise.

        :param hands: Tuple[Iterable[str], Iterable[str]]
        :return: int
        '''
        pass


class Sum(Rule):
    def __init__(self):
        pass

    def value(self, card: str) -> int:
        return strToValue[card.split(DELIMITER)[0]]

    def sum(self, hand: Iterable[str]) -> int:
        return sum(map(self.value, hand))

    def whoWins(self, hands: Tuple[Iterable[str], Iterable[str]]) -> int:
        return 0 if sum(self.value(card) for card in hands[0]) >= sum(self.value(card) for card in hands[1]) else 1


class Flush(Rule):
    def __init__(self):
        pass

    def whoWins(self, hands: Tuple[Iterable[str], Iterable[str]]) -> int:
        return 0 if 1 == len(set(card.split(DELIMITER)[2] for card in hands[0])) else 1


class Oracle:
    def __init__(self, handSize: int = 2, cards: int = 10, shapes: List[str] = ['BELLS', 'HEARTS', 'ACORNS'], rule: Rule = Sum(), samples: int = 10, seed: int = None):
        '''
        Create a new oracle using following parameters:
            handSize    # of cards on a player's hand
            cards       # of cards (1-13)
            shapes      iterable of strings representing shapes in the game
            rule        rule determining the winner from raw cards
            samples     # of samples to be generated
            seed        used for seeding random hands generation if given

        :param handSize: int
        :param cards: int
        :param shapes: Tuple of str
        :param rule: Rule
        :param samples: int
        :param seed: int
        '''
        self.handSize: int = handSize
        self.cards: int = cards
        self.shapes: List[str] = shapes
        self.rule: Rule = rule
        self.samples: int = samples

        Oracle.checkInput(cards, shapes, DELIMITER)

        # cards generation
        # value _ of _ shape
        cards = ["{}{}OF{}{}".format(valueToNumber[value + 2], DELIMITER, DELIMITER, shape) for value in range(0, cards) for shape in shapes]

        if 2 * handSize > len(cards):
            raise ValueError("there are not enough cards for this hand size")

        self.hands: List[Tuple[List[str], List[str]]] = []

        r = random
        if seed:
            r = random.Random(x=seed)
        for _ in range(0, samples):
            r.shuffle(cards)
            self.hands.append((cards[0:handSize], cards[handSize:2 * handSize]))

    @staticmethod
    def checkInput(cards: int, shapes: List[str], delimiter: str) -> None:
        # input checking
        for shape in shapes:
            for value in shape:
                if delimiter in value:
                    raise ValueError("The substring '{}' can't be used for colors nor shapes names as it is used as a delimiter.".format(delimiter))
        if cards + 1 not in valueToNumber:
            raise ValueError("At most 13 cards are available!")

    def __iter__(self):
        for idx in range(0, len(self.hands)):
            self.idx = idx
            yield self.hands[idx]

    def submitAnswer(self, answer: int) -> int:
        '''
        Given the answer (saying whether the first (0) or the second (1) player has won), the oracle returns a reward for this answer (prediction) by returning 0 and -1 for correct and incorrect prediction respectively.

        :param answer: int
        :return: int
        '''
        return 0 if answer == self.rule.whoWins(self.hands[self.idx]) else -1

from typing import Tuple, List, Union, Callable

from src.utils import strToValue
from src.engine import subsumes, lgg
from src.folParsing import parseClause
from src.logic import Clause


class Agent:
    '''
    Hi, am an generalizing agent and we will spend some time together. 
    In order for you to get points for this assignment, you have to 
    make me intelligent (again), so I am capable of learning which of the
    two cards-gambling players wins. So, let's implement the methods 
    stated in the PDF, namely receiveSample, receiveReward and
    getHypothesis. There are moreover similar to the ones in the first 
    assignment. The last one is a new one -- the environment just want
    to see what concept I'm currently thinking about.
    '''

    def __init__(self):
        self.hypothesis: Clause = Clause([])
        self.last_obs: Clause = Clause([])

    def receiveSample(self, hands: Tuple[List[str], List[str]]) -> int:
        '''
        After receiving a sample (tuple of players' hands), the agent returns who wins, i.e. 0 for winning the first player or 1 for winning the second player.
        
        :param hands: Tuple[List[str], List[str]]
        :return: int
        '''
        hand1, hand2 = self._convert_hands(hands)
        print(f'Player 0 hand: {", ".join([str(card) for card in hand1])}')
        print(f'Player 1 hand: {", ".join([str(card) for card in hand2])}')
        obs = self._sample_to_clause((hand1, hand2))
        print(f'Sample clause {str(obs)}')
        self.last_obs = obs
        if len(self.hypothesis.literals) == 0:
            return 0

        return 1 if subsumes(self.hypothesis, obs) else 0

    def receiveReward(self, reward: int) -> None:
        '''
        By calling this method the agent gets feedback whether his last decision
        was right (0) or wrong (-1). Upon wrong decision, i.e. negative reward
        it should generalize.
        
        :param reward: int 
        :return: 
        '''
        if reward == -1:
            if len(self.hypothesis.literals) == 0:
                self.hypothesis = self.last_obs
            else:
                self.hypothesis = lgg(self.hypothesis, self.last_obs)

    def getHypothesis(self) -> str:
        '''
        Call this function to get string representation of current agent's hypothesis.

        :rtype: str
        '''
        return str(self.hypothesis)

    def _sample_to_clause(self, hands: Tuple[List['Card'], List['Card']]) -> Clause:
        hand_p0, hand_p1 = hands
        func_val_0_list = [self._func_val(card) for card in hand_p0]
        func_val_1_list = [self._func_val(card) for card in hand_p1]
        literals: List[str] = [self._pred_player_cards(0, *hand_p0), self._pred_player_cards(1, *hand_p1)]
        hand_vals_0 = [card.value for card in hand_p0]
        hand_vals_1 = [card.value for card in hand_p1]
        # compare sum of cards with greater or equal
        literals.append(self._greater_or_equal(sum(hand_vals_0), sum(hand_vals_1), self._func_sum(*func_val_0_list),
                                               self._func_sum(*func_val_1_list)))
        # equal by shapes and values by equal
        for i, (card0, card1) in enumerate(zip(hand_p0, hand_p1)):
            if i != 0:
                # compare first card shape with other cards shapes by equal
                literals.append(self._equal(hand_p0[0].shape, card0.shape, self._func_shape(hand_p0[0]),
                                            self._func_shape(card0)))

            for j, (c0, c1) in enumerate(zip(hand_p0, hand_p1)):
                if j <= i:
                    continue
                # compare values of all cards
                literals.append(self._equal(card0.value, c0.value, self._func_val(card0), self._func_val(c0)))
        # compare max cards with greater or equal
        literals.append(self._greater_or_equal(max(hand_vals_0), max(hand_vals_1), self._func_max(*func_val_0_list),
                                               self._func_max(*func_val_1_list)))
        return parseClause(', '.join(literals))

    def _equal(self, x_val, y_val, x_arg, y_arg):
        if x_val == y_val:
            return self._pred_equal(x_arg, y_arg)
        else:
            return self._pred_equal(x_arg, y_arg, negation=True)

    def _greater_or_equal(self, x: int, y: int, x_arg: str, y_arg: str):
        if x > y:
            return self._pred_greater(x_arg, y_arg)
        elif x == y:
            return self._pred_equal(x_arg, y_arg)
        else:
            return self._pred_greater(y_arg, x_arg)

    def _convert_hands(self, hands: Tuple[List[str], List[str]]) -> Tuple[List['Card'], List['Card']]:
        return [Card(card, f'a{i}') for i, card in enumerate(hands[0])], [Card(card, f'b{i}') for i, card in
                                                                          enumerate(hands[1])]

    def _pred_greater(self, x: str, y: str, negation=False) -> str:
        return f'{"!" if negation else ""}Greater({x}, {y})'

    def _pred_equal(self, x: str, y: str, negation=False) -> str:
        return f'{"!" if negation else ""}Equals({x}, {y})'

    def _pred_player_cards(self, player: int, *cards: 'Card'):
        return f'CardsP{player}({", ".join([card.var for card in cards])})'

    def _func_val(self, card: 'Card') -> str:
        return f'val({card.var})'

    def _func_sum(self, *args: str) -> str:
        return f'sum({", ".join(args)})'

    def _func_shape(self, card: 'Card') -> str:
        return f'shape({card.var})'

    def _func_max(self, *args: str) -> str:
        return f'max({", ".join(args)})'


class Card:
    def __init__(self, card: str, var: str):
        val_shape = card.split('_')
        self.value: int = strToValue[val_shape[0]]
        self.shape: str = val_shape[2]
        self.name: str = card
        self.var = var

    def __str__(self):
        return f'{self.value}_{self.shape}'

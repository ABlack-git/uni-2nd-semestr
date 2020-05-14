from itertools import product, combinations
from cards import Card
import math


# You may import any objects from the standard library
#
# The implementation MUST NOT produce any side effects outside the agent instance and doing that may be considered
# cheating.

class Agent:
    """
    The API for the Agent is the following:

    The method receiveSample(cards) is called on the agent infroming which cards have been dealt.
    It should return the number of the player which has won according to the Agent's hypothesis.

    Then the method receiveReward(reward) is called informing the agent whether the answer was correct or not.
    reward = 1 for correct answer and 0 for incorrect. The method receiveReward() should return a boolean value
    indicating whether more samples are desired
    """

    def __init__(self):
        # Initialize your hypothesis.
        self.s = 2
        self.iteration = 0
        self.variables = list(product((True, False), Card, range(2)))
        # generate clauses
        self.clauses = list(combinations(self.variables, self.s))
        # remove self resolving clauses
        self.clauses = [x for x in self.clauses if
                        not (x[0][1] == x[1][1] and x[0][2] == x[1][2] and x[0][0] != x[1][0])]
        # add clauses of length 1
        self.clauses = self.clauses + [(x,) for x in self.variables]
        self.eps = 0.05
        self.delta = 0.05
        self.num_samples = round(len(self.clauses) / self.eps * math.log(len(self.clauses) / self.delta))
        self.clauses_eval = None
        print(f"Initial number of clauses: {len(self.clauses)}")
        print(f"Samples required to learn: {self.num_samples}")

    def receiveSample(self, cards):
        self.clauses_eval = [any(
            has_card == ((card, player) in cards)
            for (has_card, card, player) in clause
        ) for clause in self.clauses]
        return int(all(self.clauses_eval))

    def remove_clauses(self):
        self.clauses = [c for i, c in enumerate(self.clauses) if self.clauses_eval[i]]

    def receiveReward(self, reward):
        if reward == -1:
            self.remove_clauses()
        self.iteration += 1
        # In practice we can use fewer examples to satisfy criteria than from theoretical bound
        return self.iteration < 0.2 * self.num_samples

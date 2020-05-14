#!/usr/bin/env python
import random
from itertools import product
from cards import Card
from agent import Agent


class Oracle:
    def __init__(self, s, k):
        self.count = 0
        self.correctAnswers = 0
        self.genRules(s, k)

    def __enter__(self):
        return self

    def getSample(self, n=3, players=2):
        cards = random.sample(list(Card), n * players)
        labels = [j for j in range(players) for _ in range(n)]
        self.sample = list(zip(cards, labels))
        return self.sample

    def genRules(self, clauseMaxLen, nClauses, players=2):
        domain = set(product(Card, range(players)))
        self.rules = []
        for _ in range(nClauses):
            s = random.sample(domain, random.randint(1, clauseMaxLen))
            domain -= set(s)
            self.rules.append(tuple((random.choice((False, True)), card) for card in sorted(s)))

    @staticmethod
    def winner(rules, cards):
        return int(all(
            any(
                polarity == (card in cards)
                for (polarity, card) in clause
            )
            for clause in rules))

    def submitAnswer(self, player):
        won = self.winner(self.rules, self.sample)
        r = 0 if player == won else -1
        self.count += 1
        self.correctAnswers += r + 1
        return r

    def stats(self):
        return (self.correctAnswers / self.count) * 100, self.count

    def __exit__(self, *a):
        print("Exitting session with performance: %.2f%%\nTotal requested samples: %d" % self.stats())


def iterate(oracle, agent):
    sample = oracle.getSample()
    answer = agent.receiveSample(sample)
    correctAnswers = oracle.submitAnswer(answer)
    return agent.receiveReward(correctAnswers)


def main():
    sizes, performances = [], []
    nIters = 100
    for _ in range(nIters):
        print('**********************')
        agent = Agent()
        with Oracle(2, 3) as oracle:
            go = iterate(oracle, agent)
            while go:
                go = iterate(oracle, agent)
            p, s = oracle.stats()
            performances.append(p)
            sizes.append(s)
        print(f"Number of clauses after agent was trained {len(agent.clauses)}")
    print("Average number of requested samples was: %.2f" % (sum(sizes) / nIters))
    print("Performance > 95%% has been reached in %.2f%% cases" % (
            sum(1 for p in performances if p > 95.0) / nIters * 100))


if __name__ == "__main__":
    main()

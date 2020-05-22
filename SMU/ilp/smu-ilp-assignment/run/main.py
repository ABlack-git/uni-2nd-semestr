from src.game import Sum, Flush, Oracle
from student.agent import Agent
from student.rules import HighCard, AtLeastOnePair


def main():
    samples = 500
    oracle = Oracle(handSize=3, cards=13, shapes=['BELLS', 'HEARTS', 'ClUBS'], samples=samples, rule=AtLeastOnePair())
    agent = Agent()

    for sample in oracle:
        answer = agent.receiveSample(sample)
        isCorrectAnswer = oracle.submitAnswer(answer)
        print(f'Answer: {answer}, reward: {isCorrectAnswer}')
        agent.receiveReward(isCorrectAnswer)
        print("agent's hypothesis\t{}".format(agent.getHypothesis()))
        print(f"{'*' * 50}")

    print("agent's hypothesis\t{}".format(agent.getHypothesis()))


if __name__ == "__main__":
    main()

from gym.wrappers import Monitor

from abstractagent import AbstractAgent
from dealeragent import DealerAgent
from evaluate import *
import gym
from gym import wrappers
from gym.envs.registration import register
from randomagent import RandomAgent
from sarsaagent import SarsaAgent
from tdagent import TDAgent


def get_env() -> Monitor:
    """
    Creates the environment. Check the OpenAI Gym documentation.

    :rtype: Environment of the blackjack game that follows the OpenAI Gym API.
    """
    environment = gym.make('smu-blackjack-v0')
    return wrappers.Monitor(environment, 'smuproject4', force=True, video_callable=False)


def train():
    simp_factor = lambda x: int(0.01 * x)
    exp_factor = 0.01
    # Train TD
    number_of_epochs_td = 250000
    env_td = get_env()
    agent_td = TDAgent(env_td, number_of_epochs_td, verbose=False)
    agent_td.train()
    agent_td.save()

    # Train SARSA
    number_of_epochs_s = 500000
    env_sarsa = get_env()
    agent_sarsa = SarsaAgent(env_sarsa, number_of_epochs_s)
    agent_sarsa.train()
    agent_sarsa.save()

    # Evaluate training
    evaluate(env_td.get_episode_rewards(), 'td', simp_factor=simp_factor(number_of_epochs_td), exp_factor=exp_factor)
    evaluate(env_sarsa.get_episode_rewards(), 'sarsa', simp_factor=simp_factor(number_of_epochs_s),
             exp_factor=exp_factor)
    evaluate_stats(agent_td.stats, 'td', simp_factor(number_of_epochs_td))
    evaluate_stats(agent_sarsa.stats, 'sarsa', simp_factor(number_of_epochs_s))
    print(agent_td)
    print(agent_sarsa)


def test():
    number_of_epochs = 50000
    env_td = get_env()
    agent_td = TDAgent(env_td, number_of_epochs, verbose=False)
    agent_td.load()
    env_sarsa = get_env()
    agent_sarsa = SarsaAgent(env_sarsa, number_of_epochs)
    agent_sarsa.load()
    env_dealer = get_env()
    agent_dealer = DealerAgent(env_dealer, number_of_epochs)
    env_rand = get_env()
    agent_rand = RandomAgent(env_rand, number_of_epochs)

    agent_sarsa.test()
    agent_dealer.test()
    agent_rand.test()

    print("SARSA results")
    evaluate(env_sarsa.get_episode_rewards(), plot=False)
    print("Dealer results")
    evaluate(env_dealer.get_episode_rewards(), plot=False)
    print("Random results")
    evaluate(env_rand.get_episode_rewards(), plot=False)

    print(agent_td)
    print(agent_sarsa)


if __name__ == "__main__":
    # Registers the environment so that it can be used
    register(
        id='smu-blackjack-v0',
        entry_point='blackjack:BlackjackEnv'
    )
    # ######################################################
    # IMPORTANT: do not modify the code above this line! ###
    # ######################################################

    # train()
    test()

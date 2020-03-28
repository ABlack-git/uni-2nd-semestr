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


if __name__ == "__main__":
    # Registers the environment so that it can be used
    register(
        id='smu-blackjack-v0',
        entry_point='blackjack:BlackjackEnv'
    )
    # ######################################################
    # IMPORTANT: do not modify the code above this line! ###
    # ######################################################

    # here you can play with the code yourself
    # for example you may want to split the code to two phases - training and testing
    # or you may want to compare two agents
    # feel free to modify the number of games played (highly recommended!)
    # ... or whatever

    number_of_epochs = 100000  # TODO do not forget to change the number of epochs

    # agent: AbstractAgent = RandomAgent(env, number_of_epochs)
    # agent: AbstractAgent = DealerAgent(env, number_of_epochs)
    env_td = get_env()
    agent_td = TDAgent(env_td, number_of_epochs, verbose=False)
    # env_sarsa = get_env()
    # agent_sarsa = SarsaAgent(env_sarsa, number_of_epochs)

    agent_td.train()
    agent_td.save()
    # agent_sarsa.train()
    # agent_sarsa.save()
    simp_factor = 500
    exp_factor = 0.1
    # in evaluate.py are some ideas that you might want to use to evaluate the agent
    # feel free to modify the code as you want to
    evaluate(env_td.get_episode_rewards(), 'td', simp_factor=simp_factor, exp_factor=exp_factor)
    print("")
    # evaluate(env_sarsa.get_episode_rewards(), 'sarsa', simp_factor=simp_factor, exp_factor=exp_factor)
    # print(agent_sarsa)

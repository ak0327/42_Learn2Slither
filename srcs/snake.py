import copy

from modules.parser import str_expected, int_expected
from modules.environment import Board
from modules.agent import QLearningAgent

import sys
import argparse
import matplotlib.pyplot as plt

import torch

from distutils.util import strtobool
from tqdm import tqdm
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def train(visual):
    env = Board()
    agent = QLearningAgent()

    sessions = 10000
    visualization_interval = sessions // 10

    max_len = 0
    max_len_itrs = 0
    max_len_rewards = 0

    max_board = None
    loss_history = []
    reward_history = []
    snake_len_history = []
    ave_len_history = []

    for session in tqdm(range(sessions), desc="Training"):
        state = env.reset()
        total_loss = 0
        total_reward = 0
        itr = 0
        done = False

        # MAX_STEPS_PER_EPISODE = 100
        while not done:
            action = agent.get_action(state)
            next_state, reward, done = env.step(action)

            loss = agent.update(state, action, reward, next_state, done)
            total_loss += loss
            total_reward += reward
            itr += 1
            state = next_state

        # if done and itr < MAX_STEPS_PER_EPISODE:
        #     total_reward -= (MAX_STEPS_PER_EPISODE - itr)

        average_loss = total_loss / itr
        loss_history.append(average_loss)
        reward_history.append(total_reward)
        snake_len_history.append(len(env.snake))

        recent_interval = min(visualization_interval, len(snake_len_history))
        recent_average_len = sum(snake_len_history[-recent_interval:]) / recent_interval
        ave_len_history.append(recent_average_len)

        if max_len < len(env.snake):
            max_len = len(env.snake)
            max_len_itrs = itr
            max_len_rewards = total_reward
            max_board = copy.deepcopy(env)

        if visual == "on" and (session + 1 == 1 or (session + 1) % visualization_interval == 0):
            q_values = agent.qnet(torch.tensor(state, dtype=torch.float32)).detach().numpy()
            env.draw_with_q_values(q_values)
            print(f"\nSession [{session + 1} / {sessions + 1}]")
            print(f"Itrs         : {itr}")
            print(f"Total Reward : {total_reward}")
            print(f"Average Loss : {average_loss:.1f}")
            print(f"Max Len      : {max_len} (Itrs:{max_len_itrs}, reward:{max_len_rewards:.2f})")
            print(f"Least Ave Len: {recent_average_len:.2f} at least {recent_interval} sessions")
            print(f"{'-' * 50}\n")

    print(f"max len: {max_len}")
    print("board:")
    max_board.draw()

    fig, (ax1, ax2, ax3, ax4) = plt.subplots(4, 1, figsize=(10, 10))

    ax1.set_xlabel('Episode')
    ax1.set_ylabel('Loss')
    ax1.plot(loss_history)

    ax2.set_xlabel('Episode')
    ax2.set_ylabel('Total Reward')
    ax2.plot(reward_history)

    ax3.set_xlabel('Episode')
    ax3.set_ylabel('Length')
    ax3.plot(snake_len_history)

    ax4.set_xlabel('Episode')
    ax4.set_ylabel('Ave Length')
    ax4.plot(ave_len_history)

    plt.tight_layout()
    plt.show()


def main(visual, random_state: int = 42):
    train(visual)


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Snake"
    )
    parser.add_argument(
        "-visual",
        type=str_expected(["on", "off"]),
        default="on",
        help="visual on or off"
    )
    parser.add_argument(
        "-load",
        type=str,
        help="Path to model load"
    )
    parser.add_argument(
        "-save",
        type=str,
        help="Path to model save"
    )
    parser.add_argument(
        "-sessions",
        type=int_expected([1, 10, 100]),
        default=10,
        help="Path to model save"
    )
    parser.add_argument(
        "-eval",
        type=strtobool,
        default=0,
        help="Eval mode: true or false"
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()
    print("args:")
    print(f" visual  : {args.visual}")
    print(f" load    : {args.load}")
    print(f" save    : {args.save}")
    print(f" sessions: {args.sessions}")
    print(f" eval    : {bool(args.eval)}")
    main(visual=args.visual)

from modules.parser import str_expected, int_expected
from modules.environment import Board
from modules.agent import QLearningAgent
from modules.io import save_agent

import argparse
import copy
import matplotlib.pyplot as plt
import random
import sys
import torch
import numpy as np

from colorama import Fore, Style
from distutils.util import strtobool
from tqdm import tqdm
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def set_seed(seed):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)


def train(visual) -> QLearningAgent:
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

    wall_collision_history = []
    body_collision_history = []
    body_empty_history = []

    green_apple_history = []
    red_apple_history = []

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

        if session + 1 == 1 or (session + 1) % 100 == 0:
            total = env.wall_collision_count + env.body_collision_count + env.body_empty_count
            if total > 0:
                wall_collision_history.append(env.wall_collision_count / total * 100)
                body_collision_history.append(env.body_collision_count / total * 100)
                body_empty_history.append(env.body_empty_count / total * 100)
            else:
                wall_collision_history.append(0)
                body_collision_history.append(0)
                body_empty_history.append(0)
            # カウンターをリセット
            env.wall_collision_count = 0
            env.body_collision_count = 0
            env.body_empty_count = 0

        green_apple_history.append(env.eat_green_apple_count)
        red_apple_history.append(env.eat_red_apple_count)

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
            state_tensor = torch.tensor(state, dtype=torch.float32)
            q_values = agent.qnet(state_tensor).detach().numpy()
            env.draw_with_q_values(q_values)
            print(f"\n{'=' * 50}")
            print(f"Session [{session + 1} / {sessions + 1}]")
            print(f" Itrs         : {itr}")
            print(f" Total Reward : {total_reward:.2f}")
            print(f" Average Loss : {average_loss:.1f}\n")

            print(f"{Fore.CYAN}"
                  f" Max Len      : {max_len} (Itrs:{max_len_itrs}, reward:{max_len_rewards:.2f})")
            print(f" Least Ave Len: {recent_average_len:.2f} at least {recent_interval} sessions\n"
                  f"{Style.RESET_ALL}")

            print("Game Over")
            print(f" Wall Collision: {wall_collision_history[-1]:.1f}%")
            print(f" Body Collision: {body_collision_history[-1]:.1f}%")
            print(f" Body Empty    : {body_empty_history[-1]:.1f}%")
            print(f"{'=' * 50}\n")

    print(f"\nMax Len: {max_len}")
    print("Board:")
    max_board.draw()

    fig, (ax1, ax2, ax3, ax4, ax5, ax6) = plt.subplots(6, 1, figsize=(10, 10))

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

    ax5.set_xlabel('Episode (x100)')
    ax5.set_ylabel('GameOver %')
    history_length = len(wall_collision_history)
    episodes = range(100, (history_length * 100) + 1, 100)
    ax5.plot(episodes, wall_collision_history, label='Wall Collision')
    ax5.plot(episodes, body_collision_history, label='Body Collision')
    ax5.plot(episodes, body_empty_history, label='Body Empty')
    ax5.legend()

    ax6.set_xlabel('Episode')
    ax6.set_ylabel('Apple')
    ax6.plot(green_apple_history, label='Green Apple')
    ax6.plot(red_apple_history, label='Red Apple')
    ax6.legend()

    plt.tight_layout()
    plt.show()

    return agent


def main(visual, random_state: int = 42):
    try:
        set_seed(random_state)
        trained_agent = train(visual)

        agent_save_path = "model/agent.pkl"
        save_agent(agent=trained_agent, path=agent_save_path)

    except Exception as e:
        print(f"Fatal error: {str(e)}")
        print("Traceback:")
        _tb = e.__traceback__
        while _tb is not None:
            _filename = _tb.tb_frame.f_code.co_filename
            _line_number = _tb.tb_lineno
            print(f"File '{_filename}', line {_line_number}")
            _tb = _tb.tb_next
        print(f"Error: {str(e)}")
        sys.exit(1)


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

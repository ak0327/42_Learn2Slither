from modules.agent import QLearningAgent
import pickle


def save_agent(agent: QLearningAgent, path: str):
    with open(path, 'wb') as f:
        pickle.dump(agent, f)
        print(f"Success: save agent to {path}")


def load_agent(path: str) -> QLearningAgent:
    with open(path, 'rb') as f:
        agent: QLearningAgent = pickle.load(f)
        print(f"Success: loat agent from {path}")
        return agent

import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm

from dezero import Model
from dezero import optimizers
from dezero import Variable
import dezero.functions as F
import dezero.layers as L


class QNet(Model):
    def __init__(self, out_dim=4):
        super().__init__()
        super().__init__()
        self.l1 = L.Linear(100)
        self.l2 = L.Linear(16)
        self.l3 = L.Linear(out_dim)

    def forward(self, x):
        x = F.relu(self.l1(x))
        x = F.relu(self.l2(x))
        x = self.l3(x)
        return x


class QLearningAgent:
    def __init__(self):
        self.gamma = 0.9
        self.lr = 0.005
        self.epsilon = 0.05
        self.action_size = 4

        self.qnet = QNet(out_dim=self.action_size)
        self.optimizer = optimizers.Adam(self.lr)
        self.optimizer.setup(self.qnet)

    def get_action(self, state):
        if np.random.rand() < self.epsilon:
            return np.random.choice(self.action_size)
        else:
            qs = self.qnet(state)
            return qs.data.argmax()

    def update(self, state, action, reward, next_state, done):
        if done:
            next_q = np.zeros(1)
        else:
            next_qs = self.qnet(next_state)
            next_q = next_qs.max(axis=1)
            next_q.unchain()

        target = reward + self.gamma * next_q
        qs = self.qnet(state)
        q = qs[:, action]
        loss = F.mean_squared_error(target, q)  # targetに近づける

        self.qnet.cleargrads()
        loss.backward()
        self.optimizer.update()
        return loss.data

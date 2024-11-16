import numpy as np

import torch
import torch.nn as nn
import torch.optim as optim


class QNet(nn.Module):
    def __init__(self, in_dim: int, out_dim: int = 4):
        super().__init__()
        self.l1 = nn.Linear(in_features=in_dim, out_features=100)
        self.l2 = nn.Linear(in_features=100, out_features=16)
        self.l3 = nn.Linear(in_features=16, out_features=out_dim)

        self._initialize_weights()

    def _initialize_weights(self):
        for layer in [self.l1, self.l2, self.l3]:
            if isinstance(layer, nn.Linear):
                nn.init.xavier_uniform_(layer.weight)
                # nn.init.kaiming_normal_(layer.weight, nonlinearity='relu')
                nn.init.zeros_(layer.bias)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = torch.relu(self.l1(x))
        x = torch.relu(self.l2(x))
        x = self.l3(x)
        return x


class QLearningAgent:
    def __init__(self):
        self.gamma = 0.9
        self.lr = 0.01

        self.epsilon = 0.1
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995

        self.action_size = 4
        self.state_features = 16

        self.qnet = QNet(in_dim=self.state_features, out_dim=self.action_size)
        self.optimizer = optim.Adam(self.qnet.parameters(), lr=self.lr)
        self.criterion = nn.MSELoss()
        # self.criterion = nn.SmoothL1Loss()

    def get_action(self, state: np.ndarray) -> int:
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)
        if np.random.rand() < self.epsilon:
            return np.random.choice(self.action_size)
        else:
            with torch.no_grad():
                qs = self.qnet(torch.tensor(state, dtype=torch.float32))
                return torch.argmax(qs).item()

    def update(
            self,
            state: np.ndarray,
            action: int,
            reward: float,
            next_state: np.ndarray,
            done: bool
    ):
        state = torch.tensor(state, dtype=torch.float32)
        next_state = torch.tensor(next_state, dtype=torch.float32)
        reward = torch.tensor(reward, dtype=torch.float32)

        if done:
            next_q = torch.tensor(0.0)
        else:
            with torch.no_grad():
                next_q = self.qnet(next_state).max()

        target = reward + self.gamma * next_q
        qs = self.qnet(state)  # (1, action_size)
        q = qs.squeeze(0)[action]  # (1, 4) -> 1次元(4,)

        loss = self.criterion(q, target)

        # loss = torch.clamp(loss, min=-1.0, max=1.0)
        self.optimizer.zero_grad()
        loss.backward()
        # torch.nn.utils.clip_grad_norm_(self.qnet.parameters(), max_norm=1.0)

        self.optimizer.step()
        return loss.item()


# from dezero import Model
# from dezero import optimizers
# from dezero import Variable
# import dezero.functions as F
# import dezero.layers as L
#
#
# class QNet(Model):
#     def __init__(self, out_dim=4):
#         super().__init__()
#         super().__init__()
#         self.l1 = L.Linear(100)
#         self.l2 = L.Linear(16)
#         self.l3 = L.Linear(out_dim)
#
#     def forward(self, x):
#         x = F.relu(self.l1(x))
#         x = F.relu(self.l2(x))
#         x = self.l3(x)
#         return x
#
#
# class QLearningAgent:
#     def __init__(self):
#         self.gamma = 0.9
#         self.lr = 0.01
#
#         self.epsilon = 0.1
#         self.epsilon_min = 0.01
#         self.epsilon_decay = 0.995
#
#         self.action_size = 4
#
#         self.qnet = QNet(out_dim=self.action_size)
#         self.optimizer = optimizers.Adam(self.lr)
#         self.optimizer.setup(self.qnet)
#
#     def get_action(self, state):
#         self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)
#         if np.random.rand() < self.epsilon:
#             return np.random.choice(self.action_size)
#         else:
#             qs = self.qnet(state)
#             return qs.data.argmax()
#
#     def update(self, state, action, reward, next_state, done):
#         if done:
#             next_q = np.zeros(1)
#         else:
#             next_qs = self.qnet(next_state)
#             next_q = next_qs.max(axis=1)
#             next_q.unchain()
#
#         target = reward + self.gamma * next_q
#         qs = self.qnet(state)
#         q = qs[:, action]
#         loss = F.mean_squared_error(target, q)  # targetに近づける
#
#         self.qnet.cleargrads()
#         loss.backward()
#         self.optimizer.update()
#         return loss.data

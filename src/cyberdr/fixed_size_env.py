"""Pads observation/action spaces to MAX_NODES=10 so one policy transfers across topology sizes."""

import numpy as np
import gymnasium as gym
from gymnasium import spaces
from .multi_agent_env import MultiAgentDefenderEnv

MAX_NODES = 10  # largest topology variant (topo_5) across topo_1..5

class FixedSizeDefenderEnv(gym.Env):
    def __init__(self, environment, attacker_profile, max_steps=50, max_nodes=MAX_NODES):
        super().__init__()
        self.inner = MultiAgentDefenderEnv(environment, attacker_profile, max_steps=max_steps)
        self.max_nodes = max_nodes
        self.real_n_nodes = self.inner.n_nodes

        self.action_space = spaces.MultiDiscrete([max_nodes + 1, max_nodes + 1])
        self.observation_space = spaces.Box(low=0, high=1, shape=(max_nodes * 2,), dtype=np.float32)

    def _pad_obs(self, obs):
        padded = np.zeros(self.max_nodes * 2, dtype=np.float32)
        padded[:len(obs)] = obs
        return padded

    def reset(self, *, seed=None, options=None):
        obs, info = self.inner.reset(seed=seed, options=options)
        return self._pad_obs(obs), info

    def step(self, action):
        detector_action = int(action[0])
        responder_action = int(action[1])
        if detector_action >= self.real_n_nodes:
            detector_action = self.real_n_nodes
        if responder_action >= self.real_n_nodes:
            responder_action = self.real_n_nodes
        obs, reward, terminated, truncated, info = self.inner.step((detector_action, responder_action))
        return self._pad_obs(obs), float(reward), terminated, truncated, info

    def render(self):
        pass

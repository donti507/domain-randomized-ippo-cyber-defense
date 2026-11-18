"""Single-role Gymnasium view (detector or responder) with the partner policy frozen (IPPO)."""
import gymnasium as gym
from gymnasium import spaces
import numpy as np


class RoleEnv(gym.Env):
    def __init__(self, inner_env_factory, role, other_model=None, max_steps=50):
        super().__init__()
        assert role in ("detector", "responder")
        self.role = role
        self.inner_env_factory = inner_env_factory
        self.other_model = other_model
        self.max_steps = max_steps
        self.inner = self.inner_env_factory()
        n = self.inner.max_nodes
        self.action_space = spaces.Discrete(n + 1)
        self.observation_space = spaces.Box(low=0, high=1, shape=(n * 2,), dtype=np.float32)
        self._last_obs = None

    def set_other_model(self, model):
        self.other_model = model

    def reset(self, *, seed=None, options=None):
        self.inner = self.inner_env_factory()
        obs, info = self.inner.reset(seed=seed, options=options)
        self._last_obs = obs
        return obs, info

    def step(self, action):
        n = self.inner.max_nodes
        if self.role == "detector":
            detector_action = int(action)
            if self.other_model is not None:
                responder_action, _ = self.other_model.predict(self._last_obs, deterministic=False)
                responder_action = int(responder_action)
            else:
                responder_action = n
        else:
            responder_action = int(action)
            if self.other_model is not None:
                detector_action, _ = self.other_model.predict(self._last_obs, deterministic=False)
                detector_action = int(detector_action)
            else:
                detector_action = n

        obs, reward, terminated, truncated, info = self.inner.step((detector_action, responder_action))
        self._last_obs = obs
        return obs, float(reward), terminated, truncated, info

    def render(self):
        pass

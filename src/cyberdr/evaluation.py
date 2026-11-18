"""Deterministic evaluation: mean reward, std, containment rate over seeded episodes."""

import numpy as np
from stable_baselines3 import PPO

def evaluate_pair(detector_model, responder_model, env_builder, n_episodes=20, max_steps=50):
    """
    env_builder: zero-arg callable returning a fresh FixedSizeDefenderEnv instance
    Runs n_episodes with deterministic policies, seeded 0..n_episodes-1.
    """
    rewards = []
    lengths = []
    contained = 0

    for ep in range(n_episodes):
        env = env_builder()
        obs, info = env.reset(seed=ep)
        ep_reward = 0.0
        steps = 0
        terminated = False
        truncated = False
        while not (terminated or truncated):
            d_action, _ = detector_model.predict(obs, deterministic=True)
            r_action, _ = responder_model.predict(obs, deterministic=True)
            obs, reward, terminated, truncated, info = env.step((int(d_action), int(r_action)))
            ep_reward += reward
            steps += 1
        rewards.append(ep_reward)
        lengths.append(steps)
        if truncated and not terminated:
            contained += 1

    return {
        "mean_reward": float(np.mean(rewards)),
        "std_reward": float(np.std(rewards)),
        "mean_length": float(np.mean(lengths)),
        "containment_rate": contained / n_episodes,
    }

def load_pair(checkpoint_dir, prefix):
    detector_model = PPO.load(f"{checkpoint_dir}/{prefix}_detector_final")
    responder_model = PPO.load(f"{checkpoint_dir}/{prefix}_responder_final")
    return detector_model, responder_model

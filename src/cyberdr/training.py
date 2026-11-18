"""Alternating Independent-PPO training loop (detector / responder, 10 rounds x 5000 steps)."""

import os
from stable_baselines3 import PPO
from .role_env import RoleEnv


def train_independent_ppo(inner_env_factory, checkpoint_dir, prefix,
                           n_rounds=10, timesteps_per_round=5000,
                           n_steps=256, batch_size=64, learning_rate=3e-4,
                           verbose=0, seed=None):
    os.makedirs(checkpoint_dir, exist_ok=True)

    detector_env = RoleEnv(inner_env_factory, role="detector", max_steps=50)
    responder_env = RoleEnv(inner_env_factory, role="responder", max_steps=50)

    detector_model = PPO("MlpPolicy", detector_env, verbose=verbose,
                          n_steps=n_steps, batch_size=batch_size, learning_rate=learning_rate, seed=seed)
    responder_model = PPO("MlpPolicy", responder_env, verbose=verbose,
                           n_steps=n_steps, batch_size=batch_size, learning_rate=learning_rate,
                           seed=None if seed is None else seed + 1)

    for round_idx in range(n_rounds):
        print(f"[{prefix}] Round {round_idx + 1}/{n_rounds} - training detector...")
        detector_env.set_other_model(responder_model)
        detector_model.learn(total_timesteps=timesteps_per_round, reset_num_timesteps=False)

        print(f"[{prefix}] Round {round_idx + 1}/{n_rounds} - training responder...")
        responder_env.set_other_model(detector_model)
        responder_model.learn(total_timesteps=timesteps_per_round, reset_num_timesteps=False)

        detector_model.save(os.path.join(checkpoint_dir, f"{prefix}_detector_round{round_idx+1}"))
        responder_model.save(os.path.join(checkpoint_dir, f"{prefix}_responder_round{round_idx+1}"))

    detector_model.save(os.path.join(checkpoint_dir, f"{prefix}_detector_final"))
    responder_model.save(os.path.join(checkpoint_dir, f"{prefix}_responder_final"))
    print(f"[{prefix}] Training complete. Final models saved to {checkpoint_dir}")
    return detector_model, responder_model

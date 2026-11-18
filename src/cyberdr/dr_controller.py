"""Domain-randomization controller: samples (topology, profile, episode seed) per training episode."""
import random

class DomainRandomizationController:
    """
    Selects a fresh (topology, attacker_profile) pairing at the start of
    each training episode, from a seeded RNG independent of the attacker's
    own _attacker_rng, so DR sampling and in-episode attacker stochasticity
    never interfere with each other.
    """
    def __init__(self, topology_variants: dict, profiles: dict,
                 training_profile_names=None, training_topology_names=None,
                 seed: int = 0):
        self.topology_variants = topology_variants
        self.profiles = profiles
        self.training_profile_names = training_profile_names or list(profiles.keys())
        self.training_topology_names = training_topology_names or list(topology_variants.keys())
        self.rng = random.Random(seed)
        self.episode_count = 0
        self.history = []
    def sample_episode_config(self):
        """
        Draws one (topology_name, profile_name, episode_seed) tuple.
        episode_seed is what gets passed to env.reset(seed=...) so the
        attacker's in-episode randomness (e.g. random_target) is itself
        reproducible given this DR draw.
        """
        topo_name = self.rng.choice(self.training_topology_names)
        profile_name = self.rng.choice(self.training_profile_names)
        episode_seed = self.rng.randint(0, 2**31 - 1)

        self.episode_count += 1
        config = {
            "topology_name": topo_name,
            "profile_name": profile_name,
            "episode_seed": episode_seed,
            "episode_index": self.episode_count,
        }
        self.history.append(config)
        return config

    def make_env(self, config, generate_topology_fn, env_class, max_steps=50, **env_kwargs):
        """
        Builds a ready-to-use env instance from a sampled config.
        generate_topology_fn: your generate_topology() function from topology_generator.py
        env_class: FixedSizeDefenderEnv (or MultiAgentDefenderEnv directly)
        """
        topo_params = self.topology_variants[config["topology_name"]]
        base_env = generate_topology_fn(**topo_params)
        profile = self.profiles[config["profile_name"]]
        env = env_class(base_env, profile, max_steps=max_steps, **env_kwargs)
        env.reset(seed=config["episode_seed"])
        return env

    def summary(self):
        from collections import Counter
        topo_counts = Counter(h["topology_name"] for h in self.history)
        profile_counts = Counter(h["profile_name"] for h in self.history)
        return {
            "total_episodes": self.episode_count,
            "topology_distribution": dict(topo_counts),
            "profile_distribution": dict(profile_counts),
        }

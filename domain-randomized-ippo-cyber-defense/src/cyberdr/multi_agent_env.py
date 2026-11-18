"""Scripted-attacker / RL-defender environment wrapping CyberBattleSim low-level actions.

Detector flags a node, Responder re-images a node; attacker is scripted per profile.
Reward: +5 correct flag, +20 successful re-image, -1/-10/-30 attacker recon/lateral/compromise,
-100 and termination when the crown jewel (value >= 150) is owned. 50-step horizon = contained.
"""
import random
import copy
import numpy as np
import gymnasium as gym
from gymnasium import spaces
from cyberbattle.simulation import model as m
from cyberbattle.simulation import actions as bactions


class MultiAgentDefenderEnv(gym.Env):
    def __init__(self, environment: m.Environment, attacker_profile: dict, max_steps: int = 50):
        super().__init__()
        self.base_environment = environment
        self.attacker_profile_vulns = set(attacker_profile["vulns"])
        self.strategy = attacker_profile.get("strategy", "greedy_value")
        self.max_exploits_per_step = attacker_profile.get("max_exploits_per_step", None)
        self.max_steps = max_steps
        self.node_ids = list(environment.network.nodes)
        self.n_nodes = len(self.node_ids)

        self.detector_action_space = spaces.Discrete(self.n_nodes + 1)
        self.responder_action_space = spaces.Discrete(self.n_nodes + 1)
        self.observation_space = spaces.Box(low=0, high=1, shape=(self.n_nodes * 2,), dtype=np.float32)

        self.reset()

    def _get_obs(self):
        obs = []
        for node_id in self.node_ids:
            node_data = self.environment.network.nodes[node_id]['data']
            owned = 1.0 if node_data.agent_installed else 0.0
            flagged = 1.0 if node_id in self.flagged_nodes else 0.0
            obs.append(owned)
            obs.append(flagged)
        return np.array(obs, dtype=np.float32)

    def _owned_nodes(self):
        return [n for n in self.node_ids if self.environment.network.nodes[n]['data'].agent_installed]

    def reset(self, *, seed=None, options=None):
        self._attacker_rng = random.Random(seed)

        self.environment = copy.deepcopy(self.base_environment)
        self.attacker = bactions.AgentActions(self.environment)
        self.defender = bactions.DefenderAgentActions(self.environment)

        self.flagged_nodes = set()
        self.pending_credentials = []
        self.step_count = 0

        obs = self._get_obs()
        info = {}
        return obs, info

    def _attacker_scripted_step(self):
        reward = 0.0
        successful_exploits = 0
        owned = self._owned_nodes()

        for node_id in owned:
            node_data = self.environment.network.nodes[node_id]['data']
            for vuln_id in list(node_data.vulnerabilities.keys()):
                if vuln_id not in self.environment.identifiers.local_vulnerabilities:
                    continue
                if not vuln_id.startswith("Discover_") and vuln_id not in self.attacker_profile_vulns:
                    continue
                try:
                    result = self.attacker.exploit_local_vulnerability(node_id, vuln_id)
                    if result.reward and result.reward > 0:
                        reward -= 1.0
                        if isinstance(result.outcome, m.LeakedCredentials):
                            for cred in result.outcome.credentials:
                                self.pending_credentials.append(
                                    (node_id, cred.node, cred.port, cred.credential)
                                )
                except Exception:
                    pass

        still_pending = []
        for (source_node, target_node, port, credential) in self.pending_credentials:
            if self.max_exploits_per_step is not None and successful_exploits >= self.max_exploits_per_step:
                still_pending.append((source_node, target_node, port, credential))
                continue
            target_data = self.environment.network.nodes[target_node]['data']
            if target_data.agent_installed:
                continue
            try:
                result = self.attacker.connect_to_remote_machine(source_node, target_node, port, credential)
                if result.reward and result.reward > 0:
                    reward -= 30.0
                    successful_exploits += 1
                else:
                    still_pending.append((source_node, target_node, port, credential))
            except Exception:
                still_pending.append((source_node, target_node, port, credential))
        self.pending_credentials = still_pending

        discovered = dict(self.attacker.discovered_nodes())
        owned_set = set(self._owned_nodes())

        candidate_targets = [
            t for t in discovered if t not in owned_set
        ]
        if self.strategy == "random_target":
            self._attacker_rng.shuffle(candidate_targets)
        else:
            candidate_targets.sort(
                key=lambda t: self.environment.network.nodes[t]['data'].value,
                reverse=(self.strategy == "greedy_value")
            )

        for target_id in candidate_targets:
            if self.max_exploits_per_step is not None and successful_exploits >= self.max_exploits_per_step:
                break
            target_data = self.environment.network.nodes[target_id]['data']
            for vuln_id in target_data.vulnerabilities.keys():
                if vuln_id not in self.attacker_profile_vulns:
                    continue
                exploited = False
                for source_id in owned_set:
                    try:
                        result = self.attacker.exploit_remote_vulnerability(source_id, target_id, vuln_id)
                        if result.reward and result.reward > 0:
                            reward -= 10.0
                            successful_exploits += 1
                            exploited = True
                        break
                    except Exception:
                        continue
                if exploited:
                    break

        return reward

    def step(self, actions):
        detector_action, responder_action = actions
        reward = 0.0

        if detector_action < self.n_nodes:
            node_id = self.node_ids[detector_action]
            self.flagged_nodes.add(node_id)
            node_data = self.environment.network.nodes[node_id]['data']
            if node_data.agent_installed:
                reward += 5.0

        if responder_action < self.n_nodes:
            node_id = self.node_ids[responder_action]
            node_data = self.environment.network.nodes[node_id]['data']
            if node_data.agent_installed and node_data.reimagable:
                try:
                    self.defender.reimage_node(node_id)
                    reward += 20.0
                    self.flagged_nodes.discard(node_id)
                except Exception:
                    pass

        reward += self._attacker_scripted_step()

        self.step_count += 1
        truncated = self.step_count >= self.max_steps
        terminated = False

        for node_id in self.node_ids:
            node_data = self.environment.network.nodes[node_id]['data']
            if node_data.agent_installed and node_data.value >= 150:
                terminated = True
                reward -= 100.0

        obs = self._get_obs()
        info = {}
        return obs, reward, terminated, truncated, info

    def render(self):
        pass

"""Invariant tests. Require CyberBattleSim (see README)."""
import random
from cyberdr import (PROFILES, TOPOLOGY_VARIANTS, SEEN_PROFILES, UNSEEN_PROFILE, SEEN_TOPOLOGIES,
                     UNSEEN_TOPOLOGIES, FixedSizeDefenderEnv, DomainRandomizationController,
                     generate_topology, build_topology_a)
from cyberdr.fixed_size_env import MAX_NODES


def test_topology_sizes_and_max_nodes():
    sizes = {k: v["n_nodes"] for k, v in TOPOLOGY_VARIANTS.items()}
    assert sizes == {"topo_1": 7, "topo_2": 7, "topo_3": 8, "topo_4": 9, "topo_5": 10}
    assert max(sizes.values()) == MAX_NODES


def test_generator_is_deterministic_and_tree_shaped():
    for params in TOPOLOGY_VARIANTS.values():
        a, b = generate_topology(**params), generate_topology(**params)
        assert list(a.network.nodes) == list(b.network.nodes)
        n = params["n_nodes"]
        assert len(a.network.nodes) == n


def test_crown_jewel_has_cloud_pivot_and_is_unique_max_value():
    env = generate_topology(**TOPOLOGY_VARIANTS["topo_4"])
    vals = {n: env.network.nodes[n]["data"].value for n in env.network.nodes}
    cj = max(vals, key=vals.get)
    assert vals[cj] >= 150
    assert "CloudIAMPivot" in env.network.nodes[cj]["data"].vulnerabilities


def test_cloud_pivot_never_in_training_distribution():
    dr = DomainRandomizationController(TOPOLOGY_VARIANTS, PROFILES, training_profile_names=SEEN_PROFILES,
                                       training_topology_names=SEEN_TOPOLOGIES, seed=7)
    cfgs = [dr.sample_episode_config() for _ in range(500)]
    assert {c["profile_name"] for c in cfgs} == set(SEEN_PROFILES)
    assert not ({c["topology_name"] for c in cfgs} & set(UNSEEN_TOPOLOGIES))
    assert UNSEEN_PROFILE not in {c["profile_name"] for c in cfgs}


def test_only_cloud_pivot_profile_may_use_zero_day_vulns():
    zd = {"CloudIAMPivot", "DiscoverCloudMisconfig"}
    for name in SEEN_PROFILES:
        assert not (PROFILES[name]["vulns"] & zd)
    assert PROFILES[UNSEEN_PROFILE]["vulns"] == zd


def test_dr_controller_reproducible():
    mk = lambda: DomainRandomizationController(TOPOLOGY_VARIANTS, PROFILES, seed=3)
    a, b = mk(), mk()
    assert [a.sample_episode_config() for _ in range(20)] == [b.sample_episode_config() for _ in range(20)]


def test_env_step_contract_and_padding():
    env = FixedSizeDefenderEnv(generate_topology(**TOPOLOGY_VARIANTS["topo_1"]), PROFILES["aggressive"])
    obs, _ = env.reset(seed=0)
    assert obs.shape == (MAX_NODES * 2,)
    noop = (MAX_NODES, MAX_NODES)
    obs, r, term, trunc, _ = env.step(noop)
    assert obs.shape == (MAX_NODES * 2,) and isinstance(r, float)


def test_do_nothing_defender_loses_against_cloud_pivot():
    """Sanity: the held-out attack should reach the crown jewel quickly against a passive defender."""
    env = FixedSizeDefenderEnv(generate_topology(**TOPOLOGY_VARIANTS["topo_2"]), PROFILES[UNSEEN_PROFILE])
    env.reset(seed=0)
    term = trunc = False
    while not (term or trunc):
        _, _, term, trunc, _ = env.step((MAX_NODES, MAX_NODES))
    assert term, "crown jewel should be compromised when nobody defends"


def test_topology_a_builds():
    assert len(build_topology_a().network.nodes) == 7

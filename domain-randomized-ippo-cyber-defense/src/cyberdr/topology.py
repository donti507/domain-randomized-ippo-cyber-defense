"""Procedural topology generator (random rooted trees) and the five topology variants.

topo_1..topo_3 are the *seen* (DR training) topologies; topo_4, topo_5 are held out.
Every crown jewel carries the CloudIAMPivot vulnerability used by the held-out
`cloud_pivot` attacker profile (zero-day probe).
"""
import random
from cyberbattle.simulation import model as m

default_firewall = m.FirewallConfiguration(
    incoming=[
        m.FirewallRule("RDP", m.RulePermission.ALLOW),
        m.FirewallRule("SSH", m.RulePermission.ALLOW),
        m.FirewallRule("HTTPS", m.RulePermission.ALLOW),
    ],
    outgoing=[
        m.FirewallRule("RDP", m.RulePermission.ALLOW),
        m.FirewallRule("SSH", m.RulePermission.ALLOW),
        m.FirewallRule("HTTPS", m.RulePermission.ALLOW),
    ]
)

REMOTE_VULN_POOL = [
    ("BruteForceRDP", "RDP", 0.8), ("WeakSSH", "SSH", 0.7), ("ExploitSMB", "SSH", 0.5),
    ("SQLInjection", "HTTPS", 0.4), ("BruteForceAdminRDP", "RDP", 0.5),
    ("CredentialReuse", "SSH", 0.65), ("ExposedBackupCreds", "HTTPS", 0.5),
    ("PassTheHash", "RDP", 0.55), ("WebShell", "HTTPS", 0.7),
    ("PhishingPayload", "HTTPS", 0.4), ("WeakMonitoringAPI", "HTTPS", 0.5),
]

def generate_topology(n_nodes, seed, branching=2, min_value=10, max_value=140, crown_jewel_value=180):
    rng = random.Random(seed)
    names = ["EntryPoint"] + [f"Node_{i}" for i in range(1, n_nodes)]

    parent_of = {}
    children_of = {name: [] for name in names}
    depth_of = {"EntryPoint": 0}
    available_parents = [names[0]]
    for name in names[1:]:
        parent = rng.choice(available_parents)
        parent_of[name] = parent
        depth_of[name] = depth_of[parent] + 1
        children_of[parent].append(name)
        if len(children_of[parent]) < branching and parent not in available_parents:
            available_parents.append(parent)
        available_parents.append(name)

    # Pick the crown jewel: the deepest node (most hops from EntryPoint = most
    # defender warning time). Ties broken deterministically by name for reproducibility.
    non_root = [n for n in names if n != "EntryPoint"]
    max_depth = max(depth_of[n] for n in non_root)
    deepest_candidates = sorted([n for n in non_root if depth_of[n] == max_depth])
    crown_jewel = rng.choice(deepest_candidates)

    nodes = {}
    used_remote_ids = set()
    used_local_ids = set()

    for name in names:
        vulns = {}
        if children_of[name]:
            local_id = "Discover_" + name
            vulns[local_id] = m.VulnerabilityInfo(
                description="Discover child nodes from " + name,
                type=m.VulnerabilityType.LOCAL,
                outcome=m.LeakedNodesId(list(children_of[name])),
                rates=m.Rates(successRate=1.0),
                cost=1.0,
            )
            used_local_ids.add(local_id)

        if name == "EntryPoint":
            vulns["DiscoverCloudMisconfig"] = m.VulnerabilityInfo(
                description="Cloud IAM misconfiguration exposes a direct path to the crown-jewel asset",
                type=m.VulnerabilityType.LOCAL,
                outcome=m.LeakedNodesId([crown_jewel]),
                rates=m.Rates(successRate=1.0),
                cost=1.0,
            )
            used_local_ids.add("DiscoverCloudMisconfig")

        if name != "EntryPoint":
            vuln_id, port, rate = REMOTE_VULN_POOL[rng.randrange(len(REMOTE_VULN_POOL))]
            vulns[vuln_id] = m.VulnerabilityInfo(
                description=vuln_id + " on " + name,
                type=m.VulnerabilityType.REMOTE,
                outcome=m.LateralMove(),
                rates=m.Rates(successRate=rate),
                cost=1.0,
            )
            used_remote_ids.add(vuln_id)
            services = [m.ListeningService(port)]
            value = crown_jewel_value if name == crown_jewel else rng.randint(min_value, max_value)
            if name == crown_jewel:
                vulns["CloudIAMPivot"] = m.VulnerabilityInfo(
                    description="Zero-day cloud IAM pivot directly to " + name,
                    type=m.VulnerabilityType.REMOTE,
                    outcome=m.LateralMove(),
                    rates=m.Rates(successRate=0.6),
                    cost=1.0,
                )
                used_remote_ids.add("CloudIAMPivot")
        else:
            services = [m.ListeningService("HTTPS")]
            value = 0

        nodes[name] = m.NodeInfo(
            services=services,
            value=value,
            properties=[],
            agent_installed=(name == "EntryPoint"),
            reimagable=(name != "EntryPoint"),
            firewall=default_firewall,
            vulnerabilities=vulns,
        )

    network = m.create_network(nodes)

    identifiers = m.Identifiers(
        ports=["HTTPS", "RDP", "SSH"],
        properties=[],
        local_vulnerabilities=sorted(used_local_ids),
        remote_vulnerabilities=sorted(used_remote_ids),
    )

    env = m.Environment(network=network, vulnerability_library=dict([]), identifiers=identifiers)
    return env

TOPOLOGY_VARIANTS = {
    "topo_1": dict(n_nodes=7, seed=101, branching=2),
    "topo_2": dict(n_nodes=7, seed=202, branching=3),
    "topo_3": dict(n_nodes=8, seed=303, branching=2),
    "topo_4": dict(n_nodes=9, seed=404, branching=2),
    "topo_5": dict(n_nodes=10, seed=505, branching=3),
}


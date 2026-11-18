"""Hand-authored 7-node topology A, used ONLY by the fixed-scenario baseline."""
from cyberbattle.simulation import model as m


def build_topology_a() -> m.Environment:

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

    nodes = {
        "EntryPoint": m.NodeInfo(
            services=[m.ListeningService("HTTPS")],
            value=0,
            properties=["Windows", "ExposedToInternet"],
            agent_installed=True,
            reimagable=False,
            firewall=default_firewall,
            vulnerabilities=dict(
                DiscoverWorkstations=m.VulnerabilityInfo(
                    description="Scan local network to discover workstations",
                    type=m.VulnerabilityType.LOCAL,
                    outcome=m.LeakedNodesId(["Workstation_1", "Workstation_2"]),
                    rates=m.Rates(successRate=1.0),
                    cost=1.0
                )
            )
        ),

        "Workstation_1": m.NodeInfo(
            services=[m.ListeningService("RDP")],
            value=10,
            properties=["Windows"],
            firewall=default_firewall,
            vulnerabilities=dict(
                BruteForceRDP=m.VulnerabilityInfo(
                    description="Brute force RDP to gain access",
                    type=m.VulnerabilityType.REMOTE,
                    outcome=m.LateralMove(),
                    rates=m.Rates(successRate=0.8),
                    cost=1.0
                ),
                DiscoverFileServer=m.VulnerabilityInfo(
                    description="Discover file server from workstation",
                    type=m.VulnerabilityType.LOCAL,
                    outcome=m.LeakedNodesId(["FileServer"]),
                    rates=m.Rates(successRate=1.0),
                    cost=1.0
                )
            )
        ),

        "Workstation_2": m.NodeInfo(
            services=[m.ListeningService("SSH")],
            value=10,
            properties=["Linux"],
            firewall=default_firewall,
            vulnerabilities=dict(
                WeakSSH=m.VulnerabilityInfo(
                    description="Weak SSH password",
                    type=m.VulnerabilityType.REMOTE,
                    outcome=m.LateralMove(),
                    rates=m.Rates(successRate=0.7),
                    cost=1.0
                )
            )
        ),

        "FileServer": m.NodeInfo(
            services=[m.ListeningService("SSH")],
            value=50,
            properties=["Linux", "FileShare"],
            firewall=default_firewall,
            vulnerabilities=dict(
                ExploitSMB=m.VulnerabilityInfo(
                    description="Exploit SMB vulnerability",
                    type=m.VulnerabilityType.REMOTE,
                    outcome=m.LateralMove(),
                    rates=m.Rates(successRate=0.5),
                    cost=2.0
                ),
                DiscoverMore=m.VulnerabilityInfo(
                    description="Discover admin workstation and database server",
                    type=m.VulnerabilityType.LOCAL,
                    outcome=m.LeakedNodesId(["AdminWorkstation", "DatabaseServer"]),
                    rates=m.Rates(successRate=1.0),
                    cost=1.0
                )
            )
        ),

        "DatabaseServer": m.NodeInfo(
            services=[m.ListeningService("HTTPS")],
            value=100,
            properties=["Linux", "Database"],
            owned_string="FLAG: Database accessed",
            firewall=default_firewall,
            vulnerabilities=dict(
                SQLInjection=m.VulnerabilityInfo(
                    description="SQL injection on exposed endpoint",
                    type=m.VulnerabilityType.REMOTE,
                    outcome=m.LateralMove(),
                    rates=m.Rates(successRate=0.4),
                    cost=3.0
                )
            )
        ),

        "AdminWorkstation": m.NodeInfo(
            services=[m.ListeningService("RDP")],
            value=80,
            properties=["Windows", "AdminHost"],
            firewall=default_firewall,
            vulnerabilities=dict(
                BruteForceAdminRDP=m.VulnerabilityInfo(
                    description="Brute force RDP into admin workstation",
                    type=m.VulnerabilityType.REMOTE,
                    outcome=m.LateralMove(),
                    rates=m.Rates(successRate=0.5),
                    cost=2.0
                ),
                StealAdminCreds=m.VulnerabilityInfo(
                    description="Steal cached admin credentials, revealing Domain Controller",
                    type=m.VulnerabilityType.LOCAL,
                    outcome=m.LeakedCredentials(credentials=[
                        m.CachedCredential(node="DomainController", port="RDP", credential="admin_pass")
                    ]),
                    rates=m.Rates(successRate=0.7),
                    cost=2.0
                )
            )
        ),

        "DomainController": m.NodeInfo(
            services=[m.ListeningService("RDP", allowedCredentials=["admin_pass"])],
            value=200,
            properties=["Windows", "DomainController"],
            owned_string="FLAG: Domain Controller compromised",
            firewall=default_firewall,
            vulnerabilities=dict()
        ),
    }

    network = m.create_network(nodes)

    ENV_IDENTIFIERS = m.Identifiers(
        ports=["HTTPS", "RDP", "SSH"],
        properties=["Windows", "Linux", "ExposedToInternet", "FileShare", "Database", "AdminHost", "DomainController"],
        local_vulnerabilities=["DiscoverWorkstations", "DiscoverFileServer", "DiscoverMore", "StealAdminCreds"],
        remote_vulnerabilities=["BruteForceRDP", "WeakSSH", "ExploitSMB", "SQLInjection", "BruteForceAdminRDP"],
    )

    env = m.Environment(
        network=network,
        vulnerability_library=dict([]),
        identifiers=ENV_IDENTIFIERS
    )
    return env

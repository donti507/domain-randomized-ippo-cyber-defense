"""Scripted attacker profiles. `cloud_pivot` is the held-out zero-day probe."""
PROFILES = {
    "aggressive": {
        "vulns": {
            "BruteForceRDP", "WeakSSH", "ExploitSMB", "SQLInjection", "BruteForceAdminRDP",
            "CredentialReuse", "ExposedBackupCreds", "PassTheHash",
            "WebShell", "PhishingPayload", "WeakMonitoringAPI",
        },
        "strategy": "greedy_value",
        "max_exploits_per_step": None,
    },
    "stealthy": {
        "vulns": {
            "BruteForceRDP", "WeakSSH", "ExploitSMB", "SQLInjection", "BruteForceAdminRDP",
            "CredentialReuse", "ExposedBackupCreds", "PassTheHash",
            "WebShell", "PhishingPayload", "WeakMonitoringAPI",
        },
        "strategy": "low_value_first",
        "max_exploits_per_step": 1,
    },
    "opportunistic": {
        "vulns": {
            "BruteForceRDP", "WeakSSH", "ExploitSMB", "SQLInjection", "BruteForceAdminRDP",
            "CredentialReuse", "ExposedBackupCreds", "PassTheHash",
            "WebShell", "PhishingPayload", "WeakMonitoringAPI",
        },
        "strategy": "random_target",
        "max_exploits_per_step": 2,
    },
    "cloud_pivot": {
        "vulns": {"CloudIAMPivot", "DiscoverCloudMisconfig"},
        "strategy": "greedy_value",
        "max_exploits_per_step": None,
    },
}



SEEN_PROFILES = ["aggressive", "stealthy", "opportunistic"]
UNSEEN_PROFILE = "cloud_pivot"

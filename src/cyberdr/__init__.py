"""cyberdr: domain-randomized Independent-PPO Detector/Responder defense in CyberBattleSim."""
from .topology import generate_topology, TOPOLOGY_VARIANTS
from .profiles import PROFILES, SEEN_PROFILES, UNSEEN_PROFILE
from .fixed_size_env import FixedSizeDefenderEnv
from .dr_controller import DomainRandomizationController
from .handcrafted import build_topology_a

SEEN_TOPOLOGIES = ["topo_1", "topo_2", "topo_3"]
UNSEEN_TOPOLOGIES = ["topo_4", "topo_5"]

__version__ = "1.0.0"

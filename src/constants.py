from enum import Enum
class LoadBalancerType(Enum):
     ROUND_ROBIN = 1
     UTILISATION_AWARE = 2
class Controller(Enum):
    PI = 1
    PID = 2
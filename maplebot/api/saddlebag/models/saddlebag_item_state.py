from enum import Enum


class SaddlebagItemState(Enum):
    STABLE = "stable"
    SPIKING = "spiking"
    INCREASING = "increasing"
    DECREASING = "decreasing"
    CRASHING = "crashing"
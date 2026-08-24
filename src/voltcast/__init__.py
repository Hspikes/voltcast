"""VoltCast: physics-informed smartphone battery endurance simulation."""

from .model import (
    BatteryParameters,
    OperatingPoint,
    SimulationResult,
    open_circuit_voltage,
    simulate,
)
from .profiles import StepPoint, StepPowerProfile

__all__ = [
    "BatteryParameters",
    "OperatingPoint",
    "SimulationResult",
    "StepPoint",
    "StepPowerProfile",
    "open_circuit_voltage",
    "simulate",
]

__version__ = "0.1.0"

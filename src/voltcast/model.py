"""Continuous-time two-RC battery model with constant-power coupling."""

from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import Path
import csv
import math

from .profiles import StepPowerProfile


@dataclass(frozen=True)
class BatteryParameters:
    """Illustrative parameters for a single-cell smartphone Li-ion battery.

    The defaults are a transparent demonstration calibration, not a device
    characterization. Replace them with measurements before drawing hardware
    conclusions.
    """

    capacity_ah: float = 4.30
    r0_ohm: float = 0.055
    r1_ohm: float = 0.018
    c1_f: float = 2_400.0
    r2_ohm: float = 0.012
    c2_f: float = 12_000.0
    cutoff_voltage_v: float = 3.00
    ocv_min_v: float = 3.00
    ocv_span_v: float = 1.20

    def __post_init__(self) -> None:
        positive = {
            "capacity_ah": self.capacity_ah,
            "r0_ohm": self.r0_ohm,
            "r1_ohm": self.r1_ohm,
            "c1_f": self.c1_f,
            "r2_ohm": self.r2_ohm,
            "c2_f": self.c2_f,
            "ocv_span_v": self.ocv_span_v,
        }
        for name, value in positive.items():
            if not math.isfinite(value) or value <= 0:
                raise ValueError(f"{name} must be finite and positive")
        if not self.ocv_min_v < self.ocv_min_v + self.ocv_span_v:
            raise ValueError("the OCV range must be increasing")
        if not self.ocv_min_v <= self.cutoff_voltage_v < self.ocv_min_v + self.ocv_span_v:
            raise ValueError("cutoff voltage must lie inside the OCV range")

    def aged(self, capacity_retention: float = 0.82, resistance_growth: float = 2.5) -> "BatteryParameters":
        """Return a simple aged-battery variant for controlled comparisons."""

        if not 0 < capacity_retention <= 1:
            raise ValueError("capacity_retention must be in (0, 1]")
        if resistance_growth < 1:
            raise ValueError("resistance_growth must be at least 1")
        return replace(
            self,
            capacity_ah=self.capacity_ah * capacity_retention,
            r0_ohm=self.r0_ohm * resistance_growth,
            r1_ohm=self.r1_ohm * math.sqrt(resistance_growth),
            r2_ohm=self.r2_ohm * math.sqrt(resistance_growth),
        )


@dataclass(frozen=True)
class OperatingPoint:
    power_w: float
    ocv_v: float
    current_a: float
    terminal_voltage_v: float
    discriminant: float


@dataclass(frozen=True)
class Sample:
    time_s: float
    soc: float
    power_w: float
    current_a: float
    ocv_v: float
    terminal_voltage_v: float
    polarization_fast_v: float
    polarization_slow_v: float
    support_margin: float


@dataclass(frozen=True)
class SimulationResult:
    profile_name: str
    initial_soc: float
    stop_time_s: float
    stop_reason: str
    samples: tuple[Sample, ...]

    @property
    def time_to_empty_h(self) -> float:
        return self.stop_time_s / 3_600.0

    @property
    def final_soc(self) -> float:
        return self.samples[-1].soc if self.samples else self.initial_soc

    def write_csv(self, path: str | Path) -> None:
        destination = Path(path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        with destination.open("w", newline="", encoding="utf-8") as stream:
            writer = csv.writer(stream, lineterminator="\n")
            writer.writerow(
                [
                    "time_s",
                    "soc",
                    "power_w",
                    "current_a",
                    "ocv_v",
                    "terminal_voltage_v",
                    "polarization_fast_v",
                    "polarization_slow_v",
                    "support_margin",
                ]
            )
            for sample in self.samples:
                writer.writerow(
                    [
                        f"{sample.time_s:.3f}",
                        f"{sample.soc:.8f}",
                        f"{sample.power_w:.6f}",
                        f"{sample.current_a:.8f}",
                        f"{sample.ocv_v:.8f}",
                        f"{sample.terminal_voltage_v:.8f}",
                        f"{sample.polarization_fast_v:.8f}",
                        f"{sample.polarization_slow_v:.8f}",
                        f"{sample.support_margin:.8f}",
                    ]
                )


def open_circuit_voltage(soc: float, parameters: BatteryParameters) -> float:
    """A smooth monotonic demonstration OCV curve over normalized SOC."""

    bounded_soc = min(1.0, max(0.0, soc))
    shaped_soc = 0.12 * math.sqrt(bounded_soc) + 0.88 * bounded_soc
    return parameters.ocv_min_v + parameters.ocv_span_v * shaped_soc


def operating_point(
    power_w: float,
    soc: float,
    polarization_fast_v: float,
    polarization_slow_v: float,
    parameters: BatteryParameters,
) -> OperatingPoint | None:
    """Solve ``P = V_terminal * I`` for the stable constant-power root."""

    ocv_v = open_circuit_voltage(soc, parameters)
    effective_voltage_v = ocv_v - polarization_fast_v - polarization_slow_v
    discriminant = effective_voltage_v**2 - 4.0 * parameters.r0_ohm * power_w
    if discriminant <= 0:
        return None
    current_a = 0.0 if power_w == 0 else (
        effective_voltage_v - math.sqrt(discriminant)
    ) / (2.0 * parameters.r0_ohm)
    terminal_voltage_v = effective_voltage_v - parameters.r0_ohm * current_a
    support_margin = discriminant / max(effective_voltage_v**2, 1e-12)
    return OperatingPoint(
        power_w=power_w,
        ocv_v=ocv_v,
        current_a=current_a,
        terminal_voltage_v=terminal_voltage_v,
        discriminant=discriminant,
    )


def _derivatives(
    time_s: float,
    state: tuple[float, float, float],
    profile: StepPowerProfile,
    parameters: BatteryParameters,
) -> tuple[float, float, float]:
    soc, fast_v, slow_v = state
    point = operating_point(profile.power_at(time_s), soc, fast_v, slow_v, parameters)
    if point is None:
        raise ArithmeticError("constant-power operating point is infeasible")
    capacity_c = parameters.capacity_ah * 3_600.0
    return (
        -point.current_a / capacity_c,
        point.current_a / parameters.c1_f - fast_v / (parameters.r1_ohm * parameters.c1_f),
        point.current_a / parameters.c2_f - slow_v / (parameters.r2_ohm * parameters.c2_f),
    )


def _add_scaled(
    state: tuple[float, float, float],
    derivative: tuple[float, float, float],
    scale: float,
) -> tuple[float, float, float]:
    return tuple(value + scale * slope for value, slope in zip(state, derivative))  # type: ignore[return-value]


def _rk4_step(
    time_s: float,
    state: tuple[float, float, float],
    step_s: float,
    profile: StepPowerProfile,
    parameters: BatteryParameters,
) -> tuple[float, float, float]:
    k1 = _derivatives(time_s, state, profile, parameters)
    k2 = _derivatives(time_s + step_s / 2, _add_scaled(state, k1, step_s / 2), profile, parameters)
    k3 = _derivatives(time_s + step_s / 2, _add_scaled(state, k2, step_s / 2), profile, parameters)
    k4 = _derivatives(time_s + step_s, _add_scaled(state, k3, step_s), profile, parameters)
    return tuple(
        value + step_s * (a + 2 * b + 2 * c + d) / 6
        for value, a, b, c, d in zip(state, k1, k2, k3, k4)
    )  # type: ignore[return-value]


def simulate(
    profile: StepPowerProfile,
    parameters: BatteryParameters | None = None,
    *,
    initial_soc: float = 1.0,
    max_time_s: float = 72 * 3_600,
    step_s: float = 5.0,
    sample_interval_s: float = 60.0,
) -> SimulationResult:
    """Simulate SOC until depletion, voltage cutoff, collapse, or time limit."""

    battery = parameters or BatteryParameters()
    if not 0 < initial_soc <= 1:
        raise ValueError("initial_soc must be in (0, 1]")
    if step_s <= 0 or sample_interval_s <= 0 or max_time_s <= 0:
        raise ValueError("simulation times must be positive")

    time_s = 0.0
    state = (initial_soc, 0.0, 0.0)
    samples: list[Sample] = []
    next_sample_s = 0.0
    stop_reason = "max-time"

    while time_s <= max_time_s:
        soc, fast_v, slow_v = state
        power_w = profile.power_at(time_s)
        point = operating_point(power_w, soc, fast_v, slow_v, battery)

        if point is None:
            stop_reason = "power-collapse"
            break

        if time_s + 1e-9 >= next_sample_s or not samples:
            samples.append(
                Sample(
                    time_s=time_s,
                    soc=max(0.0, soc),
                    power_w=power_w,
                    current_a=point.current_a,
                    ocv_v=point.ocv_v,
                    terminal_voltage_v=point.terminal_voltage_v,
                    polarization_fast_v=fast_v,
                    polarization_slow_v=slow_v,
                    support_margin=point.discriminant / max(point.ocv_v**2, 1e-12),
                )
            )
            next_sample_s += sample_interval_s

        if soc <= 0:
            stop_reason = "depleted"
            break
        if point.terminal_voltage_v <= battery.cutoff_voltage_v:
            stop_reason = "voltage-cutoff"
            break
        if time_s >= max_time_s:
            break

        integration_step_s = min(step_s, max_time_s - time_s)
        next_change = profile.next_change_after(time_s)
        if next_change is not None:
            integration_step_s = min(integration_step_s, next_change - time_s)
        if integration_step_s <= 0:
            integration_step_s = min(step_s, max_time_s - time_s)

        try:
            state = _rk4_step(time_s, state, integration_step_s, profile, battery)
        except ArithmeticError:
            stop_reason = "power-collapse"
            break
        state = (max(0.0, state[0]), state[1], state[2])
        time_s += integration_step_s

    if not samples or abs(samples[-1].time_s - time_s) > 1e-9:
        soc, fast_v, slow_v = state
        point = operating_point(profile.power_at(time_s), soc, fast_v, slow_v, battery)
        if point is not None:
            samples.append(
                Sample(
                    time_s=time_s,
                    soc=max(0.0, soc),
                    power_w=point.power_w,
                    current_a=point.current_a,
                    ocv_v=point.ocv_v,
                    terminal_voltage_v=point.terminal_voltage_v,
                    polarization_fast_v=fast_v,
                    polarization_slow_v=slow_v,
                    support_margin=point.discriminant / max(point.ocv_v**2, 1e-12),
                )
            )

    return SimulationResult(
        profile_name=profile.name,
        initial_soc=initial_soc,
        stop_time_s=time_s,
        stop_reason=stop_reason,
        samples=tuple(samples),
    )

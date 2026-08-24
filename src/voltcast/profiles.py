"""Workload profiles used by the battery simulator."""

from __future__ import annotations

from bisect import bisect_right
from dataclasses import dataclass
from pathlib import Path
import csv
import math


@dataclass(frozen=True)
class StepPoint:
    """A power transition at ``time_s`` measured from simulation start."""

    time_s: float
    power_w: float

    def __post_init__(self) -> None:
        if not math.isfinite(self.time_s) or self.time_s < 0:
            raise ValueError("time_s must be finite and non-negative")
        if not math.isfinite(self.power_w) or self.power_w < 0:
            raise ValueError("power_w must be finite and non-negative")


class StepPowerProfile:
    """A zero-order-hold power profile loaded from simple CSV points."""

    def __init__(self, points: list[StepPoint] | tuple[StepPoint, ...], name: str = "profile"):
        if not points:
            raise ValueError("a power profile needs at least one point")
        ordered = tuple(points)
        if ordered[0].time_s != 0:
            raise ValueError("the first profile point must start at time 0")
        if any(right.time_s <= left.time_s for left, right in zip(ordered, ordered[1:])):
            raise ValueError("profile times must be strictly increasing")
        self.points = ordered
        self.name = name
        self._times = tuple(point.time_s for point in ordered)

    @classmethod
    def constant(cls, power_w: float, name: str = "constant") -> "StepPowerProfile":
        return cls([StepPoint(0.0, power_w)], name=name)

    @classmethod
    def from_csv(cls, path: str | Path) -> "StepPowerProfile":
        source = Path(path)
        points: list[StepPoint] = []
        with source.open(newline="", encoding="utf-8") as stream:
            reader = csv.DictReader(stream)
            required = {"time_s", "power_w"}
            if set(reader.fieldnames or ()) != required:
                raise ValueError(f"{source} must contain exactly: time_s,power_w")
            for row in reader:
                points.append(StepPoint(float(row["time_s"]), float(row["power_w"])))
        return cls(points, name=source.stem)

    def power_at(self, time_s: float) -> float:
        if time_s < 0:
            raise ValueError("time_s must be non-negative")
        index = max(0, bisect_right(self._times, time_s) - 1)
        return self.points[index].power_w

    def next_change_after(self, time_s: float) -> float | None:
        index = bisect_right(self._times, time_s)
        if index >= len(self._times):
            return None
        return self._times[index]

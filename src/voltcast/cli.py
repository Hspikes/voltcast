"""Command-line interface for VoltCast."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from .model import BatteryParameters, simulate
from .profiles import StepPowerProfile


def _load_battery(path: str | None, aged: bool) -> BatteryParameters:
    parameters = BatteryParameters()
    if path:
        with Path(path).open(encoding="utf-8") as stream:
            values = json.load(stream)
        parameters = BatteryParameters(**values)
    return parameters.aged() if aged else parameters


def _add_common_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--battery-config", help="JSON file overriding demonstration battery parameters")
    parser.add_argument("--aged", action="store_true", help="apply the documented demo aging transform")
    parser.add_argument("--step-seconds", type=float, default=5.0)
    parser.add_argument("--max-hours", type=float, default=72.0)


def _simulate_command(args: argparse.Namespace) -> int:
    profile = StepPowerProfile.from_csv(args.profile)
    result = simulate(
        profile,
        _load_battery(args.battery_config, args.aged),
        initial_soc=args.initial_soc,
        max_time_s=args.max_hours * 3_600,
        step_s=args.step_seconds,
        sample_interval_s=args.sample_seconds,
    )
    if args.output:
        result.write_csv(args.output)
    print(
        f"{profile.name}: TTE={result.time_to_empty_h:.3f} h, "
        f"final_SOC={result.final_soc:.3%}, stop={result.stop_reason}"
    )
    return 0


def _compare_command(args: argparse.Namespace) -> int:
    parameters = _load_battery(args.battery_config, args.aged)
    rows: list[dict[str, str]] = []
    for profile_path in args.profiles:
        profile = StepPowerProfile.from_csv(profile_path)
        for initial_soc in args.initial_soc:
            result = simulate(
                profile,
                parameters,
                initial_soc=initial_soc,
                max_time_s=args.max_hours * 3_600,
                step_s=args.step_seconds,
            )
            rows.append(
                {
                    "scenario": profile.name,
                    "battery": "aged-demo" if args.aged else "new-demo",
                    "initial_soc": f"{initial_soc:.2f}",
                    "tte_hours": f"{result.time_to_empty_h:.4f}",
                    "final_soc": f"{result.final_soc:.6f}",
                    "stop_reason": result.stop_reason,
                }
            )

    fieldnames = ["scenario", "battery", "initial_soc", "tte_hours", "final_soc", "stop_reason"]
    if args.output:
        destination = Path(args.output)
        destination.parent.mkdir(parents=True, exist_ok=True)
        with destination.open("w", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=fieldnames, lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)
    print("scenario\tbattery\tinitial_soc\ttte_hours\tstop_reason")
    for row in rows:
        print("\t".join(row[name] for name in ("scenario", "battery", "initial_soc", "tte_hours", "stop_reason")))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="voltcast",
        description="Physics-informed smartphone battery endurance simulation",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    simulate_parser = subparsers.add_parser("simulate", help="simulate one workload profile")
    simulate_parser.add_argument("profile")
    simulate_parser.add_argument("--initial-soc", type=float, default=1.0)
    simulate_parser.add_argument("--sample-seconds", type=float, default=60.0)
    simulate_parser.add_argument("--output", help="write the sampled trace as CSV")
    _add_common_options(simulate_parser)
    simulate_parser.set_defaults(handler=_simulate_command)

    compare_parser = subparsers.add_parser("compare", help="compare profiles and initial charge levels")
    compare_parser.add_argument("profiles", nargs="+")
    compare_parser.add_argument("--initial-soc", type=float, nargs="+", default=[1.0, 0.75, 0.5, 0.25])
    compare_parser.add_argument("--output", help="write the comparison table as CSV")
    _add_common_options(compare_parser)
    compare_parser.set_defaults(handler=_compare_command)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.handler(args)

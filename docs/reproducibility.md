# Reproducibility and evidence

## Evidence classes

VoltCast keeps three kinds of material separate:

1. **Mechanism:** equations and invariants implemented in `src/voltcast/`.
2. **Synthetic inputs:** transparent workload profiles in `scenarios/`.
3. **Demonstration outputs:** versioned CSV summaries in `artifacts/baseline/`.

No bundled result is presented as a hardware measurement.

## Reproduce the baseline

From an editable installation:

```bash
voltcast compare \
  scenarios/reading-dark.csv \
  scenarios/mixed-day.csv \
  scenarios/streaming.csv \
  scenarios/gaming.csv \
  --output artifacts/baseline/new.csv

voltcast compare \
  scenarios/reading-dark.csv \
  scenarios/mixed-day.csv \
  scenarios/streaming.csv \
  scenarios/gaming.csv \
  --aged \
  --output artifacts/baseline/aged.csv

python scripts/render_baseline_svg.py
```

Run the behavioral checks:

```bash
python -m unittest discover -s tests -v
```

## Claims supported by the baseline

The committed baseline demonstrates that the implementation:

- produces shorter endurance under heavier constant power;
- produces shorter endurance from lower initial SOC;
- exposes an earlier voltage boundary after the demo aging transform;
- preserves workload transitions in a zero-order-hold profile;
- records the state needed to inspect each stop decision.

It does not establish prediction error against a physical phone.

## Adding measured data

A measured profile must document:

- device and battery configuration;
- sampling method and units;
- operating-system and workload conditions;
- license and redistribution permission;
- preprocessing steps;
- uncertainty or repeatability information.

Do not add proprietary traces, copyrighted papers, personal identifiers, or screenshots containing account information.

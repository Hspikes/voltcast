# Model reference

VoltCast is a continuous-time research model with an explicit operating boundary. Its purpose is to make assumptions inspectable, not to hide them behind a fitted end-to-end predictor.

## State variables

The default battery contains three states:

- state of charge `z` in `[0, 1]`;
- fast polarization voltage `v1`;
- slow polarization voltage `v2`.

For current `I` and nominal capacity `Q` in coulombs:

```text
dz/dt  = -I / Q
dv1/dt = I/C1 - v1/(R1*C1)
dv2/dt = I/C2 - v2/(R2*C2)
```

The two RC branches provide short and long electrical memory without requiring an opaque time-series model.

## Open-circuit voltage

The bundled demonstration curve is monotonic:

```text
OCV(z) = Vmin + Vspan * (0.12 * sqrt(z) + 0.88 * z)
```

It spans 3.0 V to 4.2 V. This curve is intentionally simple and must be replaced with measured or published chemistry-specific data for device claims.

## Constant-power coupling

Smartphone subsystems are modeled as a requested power `P(t)`. With effective voltage

```text
Veff = OCV(z) - v1 - v2
```

and ohmic resistance `R0`, the terminal constraint is

```text
P = I * (Veff - I*R0).
```

The simulator selects the lower, stable quadratic root:

```text
I = (Veff - sqrt(Veff^2 - 4*R0*P)) / (2*R0).
```

The discriminant is an explicit support margin. If it is non-positive, the requested constant-power operating point has no real current solution and the run stops with `power-collapse`.

## Shutdown conditions

A run terminates on the first applicable condition:

1. `depleted`: SOC reaches zero;
2. `voltage-cutoff`: terminal voltage reaches the configured cutoff;
3. `power-collapse`: the constant-power quadratic has no real root;
4. `max-time`: the configured horizon ends.

This distinction matters: an aged or heavily loaded battery can reach its voltage boundary while chemical charge remains.

## Aging transform

The `--aged` option is a controlled comparison, not a calibrated degradation law. It applies:

- capacity retention of 82%;
- `R0` growth by 2.5x;
- polarization resistance growth by `sqrt(2.5)`.

For serious aging studies, replace this transform with a model fitted to calendar age, cycle count, temperature, depth of discharge, and chemistry.

## Numerical method

VoltCast uses a fixed-step fourth-order Runge-Kutta integrator. The default step is 5 seconds, and integration steps are shortened at workload transitions. This avoids runtime dependencies while remaining easy to audit.

## What is not modeled

- temperature-dependent electrochemistry;
- charge recovery and hysteresis;
- cell balancing or multi-cell packs;
- power-management controller feedback;
- parameter-estimation uncertainty;
- measurement noise and production fuel-gauge logic.

These omissions define the next research directions rather than hidden claims.

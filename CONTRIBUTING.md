# Contributing to VoltCast

VoltCast welcomes changes that make the model more transparent, reproducible, or useful.

## Good contributions

- chemistry- or device-specific calibrations with reusable source data;
- openly licensed measured workload profiles;
- uncertainty propagation and parameter sweeps;
- alternative OCV or aging models behind explicit interfaces;
- tests for physical invariants and numerical boundaries;
- documentation that distinguishes modeled, synthetic, and measured evidence.

## Pull request checklist

1. Explain the mechanism or user need being addressed.
2. State units and parameter provenance.
3. Add or update a behavioral test.
4. Run `python -m unittest discover -s tests -v`.
5. Regenerate affected baseline artifacts.
6. Avoid personal data, copyrighted source PDFs, private datasets, and unsupported benchmark claims.

Changes to default parameters must explain why the new values are a better demonstration baseline. Hardware-specific claims require reproducible validation data.

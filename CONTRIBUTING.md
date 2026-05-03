# Contributing to bms-analysis

This repository documents and analyses the GivEnergy LV BMS protocol with the goal of enabling third-party battery emulators (3rd-party LFP cell -> GivEnergy inverter) and bridges (GivEnergy battery -> standard inverter, e.g. Pylontech CAN). Contributions are very welcome -- captures, corrections, additional firmware versions, working emulator/bridge implementations.

## Scope

The repo focuses on **Low-Voltage (LV)** GivEnergy batteries, currently Gen 2 9.5 kWh family, and the inverters they speak to (AC 3.0, Gen 1 / Gen 2 / Gen 3 Hybrid). High-Voltage (HV) and All-In-One (AIO) battery families are out of scope -- they use different protocols.

The `docs/` tree is the canonical protocol reference. Wire-capture tools and analysis utilities live in `tools/`.

## What's especially welcome

- More wire captures, especially under specific conditions (charge, discharge, fault, balancing, low-SoC).
- Captures from different inverter variants.
- Additional firmware versions for static analysis cross-reference.
- Emulator and bridge implementations and test reports against real hardware.
- Corrections to field interpretations, including negative results ("PACE hypothesis X does NOT apply to GivEnergy field Y").
- Cell-monitor protocol details (the inter-pack PACE channel is incompletely documented).

## Setup for the Python tooling

The capture and analysis tools require Python 3.11+:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest
```

All tests should pass on a fresh install.

## Privacy: redact captures before sharing

Real wire captures contain a 20-character serial number in IR Block 1 bytes 0-19 (and may contain other identifiers). **Always redact captures and any pasted excerpts before sharing publicly.**

Configure your serials and IPs in `~/.givenergy-redact.toml`:

```toml
serials = ["YOUR-INVERTER-SERIAL", "YOUR-BATTERY-SERIAL"]
ips = ["192.168.X.X"]
```

Then process captures with:

```bash
python tools/redact.py path/to/capture.log --out path/to/capture.redacted.log
```

The PR template includes a redaction checklist -- please confirm before submitting captures.

If a real serial accidentally lands on the public repo, raise an issue or contact a maintainer immediately. Even closed PR diffs persist; reach out so we can pursue redaction via GitHub Support.

## Commit and PR style

- Short imperative commit messages (e.g. "Add tag.py manual + auto modes"), no AI attribution trailers.
- One logical change per commit; rebase locally to clean up before push.
- Follow test-driven development where applicable -- write the failing test first, then the implementation.
- ASCII only in source and docs (no em-dashes, Unicode arrows, smart quotes, multiplication signs, etc.). Some downstream tools expect ASCII byte streams; keeping the docs ASCII avoids surprises.
- Open PRs against `main`. Tag related issues if any.
- The PR template's privacy checklist must be ticked before merge.

## Reporting bugs and sharing captures

Use the issue templates: bug report or capture share. The capture-share template walks you through the redaction confirmation and the labelling fields needed for downstream analysis.

## License

See [`LICENSE`](LICENSE).

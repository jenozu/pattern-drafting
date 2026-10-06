# Pattern Drafting — Recovery Snapshot

This repository preserves the recoverable state of the sewing-pattern drafting project developed in ChatGPT. The first garment is a basic pants/trouser block based on the Shapes of Fabric basic pants drafting method.

## Important recovery note

The accessible conversation history retained the formulas, architecture, starter Python implementation, sample measurements, and known bug description. It did **not** retain the complete later source that produced the malformed front crotch/inseam path. This repository does not pretend that missing code was recovered. See `PROJECT_STATUS.md`.

## Current behavior

The recovered scaffold accepts waist, hip, waist-to-hip, crotch depth, waist-to-knee, waist-to-ankle, and hem circumference; calculates construction levels, crotch extensions, hem distribution and crease/grainline positions; and exports construction geometry to `pants_block.svg` in millimetres.

The intended later implementation included complete front/back outlines, Bézier crotch curves, waist/hip/side/inseam shaping, a 10 cm × 2 cm back dart, grainlines, labels, and eventually printable/export formats. Those later complete paths were not recoverable verbatim.

## Install

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
python main.py
```

Enter measurements in centimetres. Output: `pants_block.svg`.

## Reference measurements

- waist: 74 cm
- hip: 96 cm
- waist to hip: 20 cm
- crotch depth: 26 cm
- waist to knee: 60 cm
- waist to ankle: 104 cm
- hem circumference: 46 cm

## Tests

```bash
pytest -q
```

## Known bug / unfinished area

The project later reached a state where the **back pants piece drafted relatively correctly**, while the **front piece had incorrect path/line connections around the crotch-to-inseam region**. The exact later buggy path-building source was not present in recoverable history, so it has not been fabricated here.

See `PROJECT_STATUS.md` before continuing development.

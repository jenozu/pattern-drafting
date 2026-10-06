# Pattern Drafting

A Python sewing-pattern drafting project. The first implemented garment is a basic pants/trouser block based on the Shapes of Fabric basic pants drafting method.

## Current behavior

The program accepts body measurements in centimetres and generates separate front and back trouser-block outlines as SVG.

Implemented features include:

- front/back crotch extensions
- center-front and raised center-back construction
- waist, hip, crotch, knee and hem shaping
- crease/grainlines
- tutorial-derived knee placement
- separate front/back Bézier crotch and thigh curves
- 10 cm x 2 cm back dart
- debug point labels
- seam-length diagnostics
- regression tests for path continuity and core drafting rules

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

## Development status

The earlier malformed front crotch/inseam behavior is no longer represented by a single opaque SVG path. Front and back outlines now use named semantic segments with endpoint-continuity tests.

The block is still a development draft, not yet a production sewing pattern. The next stage is seam walking/equalization of the upper side seams and upper inseams, followed by physical/toile validation before adding seam allowances or printable export formats.

See `PROJECT_STATUS.md` for the technical handoff.

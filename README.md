# Pattern Drafting

A Python sewing-pattern drafting project. The first implemented garment is a basic pants/trouser block based on The Shapes of Fabric basic pants drafting method.

Source method: https://www.theshapesoffabric.com/2020/08/16/learn-how-to-draft-the-basic-pants-pattern/

## Current state

The pants block now includes:

- front/back crotch extensions
- center-front and raised center-back construction
- waist, hip, crotch, knee, and hem shaping
- tutorial-derived crease/grainlines
- tutorial-derived knee placement
- separate front/back Bezier crotch and thigh curves
- back dart located on the curved waistline
- 10 cm dart length and 2 cm dart intake
- automatic seam walking/equalization
- knee alignment notches
- 5 cm print calibration square
- clean or debug SVG output
- JSON diagnostics/report output
- input validation
- self-intersection regression tests
- multi-size regression tests
- GitHub Actions test workflow

The historical front-crotch path-mixing failure is specifically guarded against by named semantic segments, endpoint-continuity tests, and sampled self-intersection checks.

## Important limitation

This is still a base block under fit validation, not a production-ready sewing pattern.

No seam allowance is added. The next meaningful validation step is to make a toile/muslin from a correctly printed block and assess fit. Once that physical validation is complete, seam allowance, production markings, tiled PDF export, DXF export, and a user-facing UI can be added with confidence.

## Install

    python -m venv .venv

Windows:

    .venv\Scripts\activate

macOS/Linux:

    source .venv/bin/activate

Then:

    pip install -r requirements.txt

## Run interactively

    python main.py

## Run from a measurement JSON file

    python main.py --measurements examples/measurements.json --output pants_block.svg --report pants_block_report.json

Useful options:

    python main.py --measurements examples/measurements.json --clean
    python main.py --measurements examples/measurements.json --no-seam-walk

## Measurement JSON format

All values are centimetres.

    {
      "waist": 74,
      "hip": 96,
      "waist_to_hip": 20,
      "crotch_depth": 26,
      "waist_to_knee": 60,
      "waist_to_ankle": 104,
      "hem_circ": 46
    }

## Reference construction

For the reference measurements above:

- construction width: 50 cm
- crotch level: 27.5 cm
- front crotch extension: 6 cm
- back crotch extension: 9 cm
- front grainline x: 9.5 cm
- back grainline x: 40.5 cm

Before seam walking, the reconstructed reference geometry differs by roughly:

- upper side seam: 5.4 mm
- upper inseam: 3.3 mm

The automated seam-walking pass reduces both to effectively zero within the configured tolerance.

The upper inseam means knee to crotch point. The center-front/center-back crotch curve is not counted as part of the inseam.

## Tests

    pytest -q

The suite covers source construction formulas, path continuity, self-intersection detection, multiple body-size profiles, knee-placement rules, seam walking, raw/unwalked mode, dart dimensions, waist right angles, invalid measurements, and CLI SVG/report generation.

See PROJECT_STATUS.md and DESIGN_NOTES.md for the technical handoff.

# Project Status / Technical Handoff

## Current status

The repository now contains a working reconstruction of the basic front/back pants block geometry, based on the Shapes of Fabric basic pants tutorial.

The exact historical buggy revision was not recoverable verbatim, so the outline layer was rebuilt from the documented construction method rather than fabricated as "recovered" code.

## Architecture

- `main.py` — CLI input and generation entry point
- `measurements.py` — measurement/config dataclasses
- `drafting.py` — pants drafting calculations and named front/back outline segments
- `geometry.py` — unit conversion, interpolation, Bézier sampling, seam-length helpers
- `svg_export.py` — separated front/back SVG rendering, debug labels, grainlines and back dart
- `tests/` — construction and path regression tests
- `examples/measurements.json` — reference input

## Implemented construction rules

- rectangle width = 1/2 hip + 2 cm ease
- crotch level = crotch depth + 1.5 cm
- front crotch extension = (1/2 hip) / 8
- back crotch extension = front extension + 3 cm
- front center waist moves 0.5 cm inward and 1 cm down
- back center line moves 4 cm inward at the original top and extends 2.5 cm upward
- front waist width = (1/2 waist) / 2 + 1.5 cm
- back waist width = (1/2 waist) / 2 + 0.5 cm
- front grainline = midpoint between front crotch point and side seam at crotch level
- back grainline reuses the front side-to-grain distance
- hem = half chosen circumference; front -1 cm, back +1 cm
- front knee is derived from the straight crotch-to-inseam-hem guide, then moved 1 cm toward the grainline
- back knee adds 1 cm each side relative to the front knee half-width
- back dart = 10 cm long x 2 cm wide

## Regression coverage

The test suite verifies:

1. reference sample formulas
2. continuous/closed front outline
3. continuous/closed back outline
4. tutorial-derived front knee placement
5. back knee +1 cm rule
6. equal front/back lower side-seam length
7. equal front/back lower inseam length
8. back dart dimensions

## Reference sample

For waist 74 cm, hip 96 cm, waist-to-hip 20 cm, crotch depth 26 cm, waist-to-knee 60 cm, waist-to-ankle 104 cm, hem circumference 46 cm:

- construction width = 50 cm
- crotch level = 27.5 cm
- front crotch extension = 6 cm
- back crotch extension = 9 cm
- front grainline x = 9.5 cm
- back grainline x = 40.5 cm

## Remaining refinement

The major historical front-crotch path-mixing problem is structurally addressed by named, piece-local semantic segments and endpoint continuity tests.

The next important work is fit/seam refinement rather than path repair:

1. walk front/back upper side seams and equalize them
2. walk front/back upper inseams and equalize them
3. refine Bézier control points while preserving seam lengths
4. verify waistline/dart shaping against a toile or trusted drafted reference
5. add notches and seam allowance only after the base block is validated
6. later add printable PDF/DXF output and UI

Current seam diagnostics are intentionally retained in `draft["checks"]` so upper-seam differences can be measured rather than hidden.

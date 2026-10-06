# Project Status / Technical Handoff

## Recovery status

The target GitHub repository was empty when recovery began. Accessible conversation history contained the drafting formulas and starter scaffold, but not the full later source that exhibited the known front-piece path bug.

## Architecture

- `main.py` — CLI input and generation entry point
- `measurements.py` — measurement/config dataclasses
- `drafting.py` — pants drafting calculations
- `geometry.py` — unit/geometry helpers
- `svg_export.py` — SVG construction drawing
- `tests/` — formula regression checks
- `examples/measurements.json` — reference input

## Drafting methodology recovered

The project followed the Shapes of Fabric basic pants pattern tutorial.

- rectangle width = 1/2 hip + 2 cm ease
- crotch level = crotch depth + 1.5 cm
- front crotch extension = (1/2 hip) / 8
- back crotch extension = (1/2 hip) / 8 + 3 cm
- front waist width = (1/2 waist) / 2 + 1.5 cm
- back waist width = (1/2 waist) / 2 + 0.5 cm
- hem = half chosen circumference; front −1 cm, back +1 cm
- back dart intended at 10 cm long × 2 cm wide
- front crotch curve intended shallower than back; Bézier curves were the planned/used representation
- inputs in cm; SVG dimensions converted to mm

## Components known to have worked

Measurement-based construction calculations, hip/crotch/knee/hem guides, front/back crotch extensions, crease/grainline scaffold, and SVG construction output. The later back-piece geometry was remembered as drafting relatively correctly.

## Known broken behavior

The remembered later implementation had an incorrect **front pants path connection around the crotch/inseam area**. The front outline mixed or connected line/path segments incorrectly, while the back piece appeared comparatively correct.

The exact faulty later function/path sequence is NOT present in the recoverable transcript. Do not assume the simplified construction exporter in this snapshot is the buggy later implementation; it predates/under-represents that state.

## Missing / not recoverable verbatim

- complete later front outline/path code
- complete later back outline/path code
- exact Bézier control points from the buggy revision
- any Streamlit UI source, if actually implemented
- PDF/DXF exporter source, if implemented later
- sample SVG/screenshots from the later buggy revision
- original later test output

These must not be invented and labeled as recovered artifacts.

## Recommended next debugging steps

1. Reintroduce front/back outline segments as named semantic segments.
2. Render every named point and segment with temporary labels/indices.
3. Verify front traversal: center-front waist → waist/side → hip → side knee → side hem → inseam hem → inseam knee → crotch point → crotch curve → center front.
4. Ensure the front crotch curve terminates at the intended crotch point and the inseam starts at that same endpoint.
5. Assert adjacent path segments share endpoints within tolerance.
6. Keep front/back point namespaces separate to prevent cross-piece references.
7. Compare geometry against the tutorial step-by-step before adding seam allowance or more export formats.

## Scope decision

Do not hide the historical defect by redesigning the engine before reproducing it. First rebuild/locate the missing later outline logic, reproduce the front failure, add a regression test, then fix it.

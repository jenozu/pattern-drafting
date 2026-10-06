# Design Notes

## Coordinate system

All drafting geometry is stored in centimetres.

- x increases to the right
- y increases downward
- front is drafted from the left side of the shared construction rectangle
- back is drafted from the right side
- the exporter translates the pieces apart for display and printing

SVG conversion happens only at export time: 1 cm = 10 mm.

## Outline topology

Each piece is an ordered list of named semantic segments rather than one opaque SVG path.

Front order:

1. waist
2. hip side
3. upper side
4. side thigh
5. side lower leg
6. hem
7. inseam lower leg
8. inseam thigh
9. front crotch curve
10. center front

Back uses the equivalent sequence.

This is deliberate: the historical project failure involved incorrect front path connections near the crotch/inseam. Named segments allow endpoint-continuity and self-intersection tests.

## Seam definitions

For seam walking:

- lower side seam = knee to hem
- upper side seam = knee to waist
- lower inseam = knee to hem
- upper inseam = knee to crotch point

The center crotch curve is not part of the inseam. It becomes part of the center-front/center-back crotch seam when the garment is assembled.

## Automatic seam walking

The drafting tutorial requires seam lengths to be walked/equalized but does not prescribe a software algorithm.

This implementation uses conservative geometry adjustments.

For the upper inseam, if the back upper inseam is longer than the front, the back crotch point is lowered until the two lengths match. This mirrors the tutorial's explicit note that lowering the back crotch curve slightly during equalization is acceptable.

If the unusual inverse case occurs, additional back-inseam curvature is used instead of moving the front construction.

For the upper side seam, whichever seam is shorter is lengthened by bowing the cubic Bezier control points outward. Endpoints remain fixed.

All automatic adjustments are bounded by DraftConfig limits and recorded in the generated diagnostic report.

## Waistline geometry

The front and back waist Bezier curves are constructed so their starting tangent is perpendicular to the corresponding center-front/center-back seam.

The back dart is centered along the curved back-waist seam by arc length. Its legs are placed 2 cm apart along that seam, and its tip is 10 cm below the dart center.

## Topology protection

geometry.outline_self_intersections samples every Bezier into short line segments and checks non-adjacent edges for proper crossings.

It is intentionally a regression guard, not a CAD-grade exact curve-intersection solver. Its purpose is to catch failures such as a crotch segment suddenly connecting across the body of the pattern.

## Production boundary

This repository currently models a basic block, not a finished commercial sewing pattern.

Do not add seam allowance or rely on the block for final garment cutting until a physical toile has confirmed the fit. The SVG includes a 5 cm calibration square specifically to make that next validation reproducible.

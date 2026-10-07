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

## Upper inseam walking

For the upper inseam, if the back upper inseam is longer than the front, the back crotch point is lowered until the two lengths match. This mirrors the tutorial's explicit note that lowering the back crotch curve slightly during equalization is acceptable.

If the unusual inverse case occurs, additional back-inseam curvature is used instead of moving the front construction.

## C2-continuous side seam

The upper side seam is represented as three cubic Beziers sharing the construction landmarks:

- side waist
- side hip
- side crotch level
- side knee

The control points are solved as a y-parameterized cubic Hermite spline with continuous first and second derivatives at the hip and crotch joins. In practical terms, the seam has no angle kink and no abrupt curvature change at those landmarks.

The waist-end derivative is seeded from the original draft's first Bezier control handle so the source silhouette intent is retained. The knee-end derivative follows the knee-to-hem side seam.

## Bounded side-seam adjustment

Exact seam-length equality is not forced when doing so would require a visibly distorted silhouette.

If one upper side seam is shorter, the algorithm may adjust its waist-end derivative within DraftConfig.max_side_bulge. If the configured bound is reached before exact equality, the fair spline is kept and the remaining difference is recorded as residual ease.

For the reference measurements, this leaves roughly 3.2 mm residual upper side-seam ease while removing the visible back hip/seat bubble.

This is intentional: the residual must be evaluated in the physical toile rather than hidden by an artificial CAD bulge.

## Waistline geometry

The front and back waist Bezier curves are constructed so their starting tangent is perpendicular to the corresponding center-front/center-back seam.

The back dart is centered along the curved back-waist seam by arc length. Its legs are placed 2 cm apart along that seam, and its tip is 10 cm below the dart center.

## Topology protection

geometry.outline_self_intersections samples every Bezier into short line segments and checks non-adjacent edges for proper crossings.

It is intentionally a regression guard, not a CAD-grade exact curve-intersection solver. Its purpose is to catch failures such as a crotch segment suddenly connecting across the body of the pattern.

## Production boundary

This repository currently models a basic block, not a finished commercial sewing pattern.

Do not add seam allowance or rely on the block for final garment cutting until a physical toile has confirmed the fit. The SVG includes a 5 cm calibration square specifically to make that next validation reproducible.

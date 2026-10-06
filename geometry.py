from dataclasses import dataclass
from math import hypot

MM_PER_CM = 10.0
EPSILON = 1e-9

def cm_to_mm(value: float) -> float:
    return value * MM_PER_CM

@dataclass(frozen=True)
class Point:
    x: float
    y: float

    def as_tuple(self):
        return (self.x, self.y)

def distance(a, b) -> float:
    return hypot(b[0] - a[0], b[1] - a[1])

def interpolate_x_at_y(a, b, y):
    if abs(b[1] - a[1]) < EPSILON:
        raise ValueError("Cannot interpolate x on a horizontal segment")
    t = (y - a[1]) / (b[1] - a[1])
    return a[0] + t * (b[0] - a[0])

def cubic_point(p0, p1, p2, p3, t):
    u = 1.0 - t
    return (
        u**3*p0[0] + 3*u*u*t*p1[0] + 3*u*t*t*p2[0] + t**3*p3[0],
        u**3*p0[1] + 3*u*u*t*p1[1] + 3*u*t*t*p2[1] + t**3*p3[1],
    )

def cubic_derivative(p0, p1, p2, p3, t):
    u = 1.0 - t
    return (
        3*u*u*(p1[0]-p0[0]) + 6*u*t*(p2[0]-p1[0]) + 3*t*t*(p3[0]-p2[0]),
        3*u*u*(p1[1]-p0[1]) + 6*u*t*(p2[1]-p1[1]) + 3*t*t*(p3[1]-p2[1]),
    )

def cubic_length(p0, p1, p2, p3, steps=120):
    total = 0.0
    prev = p0
    for i in range(1, steps + 1):
        cur = cubic_point(p0, p1, p2, p3, i / steps)
        total += distance(prev, cur)
        prev = cur
    return total

def segment_length(seg):
    if seg["type"] == "line":
        return distance(seg["start"], seg["end"])
    if seg["type"] == "cubic":
        return cubic_length(seg["start"], seg["c1"], seg["c2"], seg["end"])
    raise ValueError(f"Unknown segment type: {seg['type']}")

def sample_segment(seg, curve_steps=24):
    if seg["type"] == "line":
        return [seg["start"], seg["end"]]
    if seg["type"] == "cubic":
        return [
            cubic_point(seg["start"], seg["c1"], seg["c2"], seg["end"], i / curve_steps)
            for i in range(curve_steps + 1)
        ]
    raise ValueError(f"Unknown segment type: {seg['type']}")

def sample_outline(segments, curve_steps=24):
    points = []
    for seg in segments:
        sampled = sample_segment(seg, curve_steps=curve_steps)
        points.extend(sampled if not points else sampled[1:])
    return points

def _orientation(a, b, c):
    return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])

def _proper_intersection(a, b, c, d, tol=1e-8):
    if any(distance(p, q) <= tol for p in (a, b) for q in (c, d)):
        return False
    o1 = _orientation(a, b, c)
    o2 = _orientation(a, b, d)
    o3 = _orientation(c, d, a)
    o4 = _orientation(c, d, b)
    return ((o1 > tol and o2 < -tol) or (o1 < -tol and o2 > tol)) and (
        (o3 > tol and o4 < -tol) or (o3 < -tol and o4 > tol)
    )

def outline_self_intersections(segments, curve_steps=24):
    points = sample_outline(segments, curve_steps=curve_steps)
    edges = list(zip(points, points[1:]))
    hits = []
    for i, (a, b) in enumerate(edges):
        for j in range(i + 1, len(edges)):
            if j == i + 1:
                continue
            if i == 0 and j == len(edges) - 1:
                continue
            c, d = edges[j]
            if _proper_intersection(a, b, c, d):
                hits.append((i, j))
    return hits

def point_on_segment_at_length(seg, target_length, samples=400):
    total = segment_length(seg)
    if target_length <= 0:
        return seg["start"]
    if target_length >= total:
        return seg["end"]

    points = sample_segment(seg, curve_steps=samples if seg["type"] == "cubic" else 1)
    travelled = 0.0
    for a, b in zip(points, points[1:]):
        step = distance(a, b)
        if travelled + step >= target_length:
            if step < EPSILON:
                return b
            ratio = (target_length - travelled) / step
            return (
                a[0] + ratio * (b[0] - a[0]),
                a[1] + ratio * (b[1] - a[1]),
            )
        travelled += step
    return seg["end"]

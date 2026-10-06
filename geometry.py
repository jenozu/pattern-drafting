from dataclasses import dataclass
from math import hypot

MM_PER_CM = 10.0

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
    if b[1] == a[1]:
        raise ValueError("Cannot interpolate x on a horizontal segment")
    t = (y - a[1]) / (b[1] - a[1])
    return a[0] + t * (b[0] - a[0])

def cubic_point(p0, p1, p2, p3, t):
    u = 1.0 - t
    return (
        u**3*p0[0] + 3*u*u*t*p1[0] + 3*u*t*t*p2[0] + t**3*p3[0],
        u**3*p0[1] + 3*u*u*t*p1[1] + 3*u*t*t*p2[1] + t**3*p3[1],
    )

def cubic_length(p0, p1, p2, p3, steps=80):
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
    raise ValueError(seg["type"])

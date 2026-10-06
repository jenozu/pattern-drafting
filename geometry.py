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

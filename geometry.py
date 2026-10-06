from dataclasses import dataclass

MM_PER_CM = 10.0

def cm_to_mm(value: float) -> float:
    return value * MM_PER_CM

@dataclass(frozen=True)
class Point:
    x: float
    y: float

    def as_tuple(self):
        return (self.x, self.y)

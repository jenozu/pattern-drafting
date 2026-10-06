import svgwrite
from geometry import cm_to_mm

def _mm(point, x_offset_cm=0.0, y_offset_cm=0.0):
    return (cm_to_mm(point[0] + x_offset_cm), cm_to_mm(point[1] + y_offset_cm))

def _path_for_segments(drawing, segments, x_offset_cm=0.0, y_offset_cm=0.0):
    sx, sy = _mm(segments[0]["start"], x_offset_cm, y_offset_cm)
    path = drawing.path(d=f"M {sx} {sy}", fill="none", stroke="black", stroke_width=2)
    for seg in segments:
        if seg["type"] == "line":
            x, y = _mm(seg["end"], x_offset_cm, y_offset_cm)
            path.push(f"L {x} {y}")
        elif seg["type"] == "cubic":
            c1x, c1y = _mm(seg["c1"], x_offset_cm, y_offset_cm)
            c2x, c2y = _mm(seg["c2"], x_offset_cm, y_offset_cm)
            ex, ey = _mm(seg["end"], x_offset_cm, y_offset_cm)
            path.push(f"C {c1x} {c1y} {c2x} {c2y} {ex} {ey}")
        else:
            raise ValueError(f"Unknown segment type: {seg['type']}")
    path.push("Z")
    return path

def _bounds(piece):
    xs = [p[0] for p in piece["points"].values()]
    ys = [p[1] for p in piece["points"].values()]
    return min(xs), max(xs), min(ys), max(ys)

def export_svg(draft, filename="pants_block.svg", debug=True):
    front = draft["pieces"]["front"]
    back = draft["pieces"]["back"]
    margin_cm = 2.0
    gap_cm = 6.0
    fminx, fmaxx, fminy, fmaxy = _bounds(front)
    bminx, bmaxx, bminy, bmaxy = _bounds(back)
    front_xoff = margin_cm - fminx
    front_yoff = margin_cm - min(0.0, fminy)
    back_xoff = front_xoff + (fmaxx - fminx) + gap_cm - bminx
    back_yoff = margin_cm - min(0.0, bminy)
    total_width_cm = back_xoff + bmaxx + margin_cm
    total_height_cm = max(front_yoff + fmaxy, back_yoff + bmaxy) + margin_cm

    drawing = svgwrite.Drawing(
        filename,
        size=(f"{cm_to_mm(total_width_cm)}mm", f"{cm_to_mm(total_height_cm)}mm"),
        viewBox=f"0 0 {cm_to_mm(total_width_cm)} {cm_to_mm(total_height_cm)}",
    )
    drawing.add(drawing.rect(insert=(0, 0), size=("100%", "100%"), fill="white"))

    for piece_name, piece, xoff, yoff in (
        ("front", front, front_xoff, front_yoff),
        ("back", back, back_xoff, back_yoff),
    ):
        drawing.add(_path_for_segments(drawing, piece["segments"], xoff, yoff))
        gx = cm_to_mm(piece["grain_x"] + xoff)
        drawing.add(drawing.line(
            start=(gx, cm_to_mm(yoff + 7)),
            end=(gx, cm_to_mm(yoff + draft["guides"]["height"] - 4)),
            stroke="gray", stroke_dasharray="8,6"
        ))
        drawing.add(drawing.text(piece_name.upper(), insert=(cm_to_mm(min(p[0] for p in piece["points"].values()) + xoff), cm_to_mm(yoff + 5)), font_size="18px"))

        dart = piece.get("markings", {}).get("dart")
        if dart:
            lx, ly = _mm(dart["left"], xoff, yoff)
            rx, ry = _mm(dart["right"], xoff, yoff)
            tx, ty = _mm(dart["tip"], xoff, yoff)
            drawing.add(drawing.line(start=(lx, ly), end=(tx, ty), stroke="black", stroke_width=1))
            drawing.add(drawing.line(start=(rx, ry), end=(tx, ty), stroke="black", stroke_width=1))

        if debug:
            for name, point in piece["points"].items():
                x, y = _mm(point, xoff, yoff)
                drawing.add(drawing.circle(center=(x, y), r=3, fill="red"))
                drawing.add(drawing.text(name, insert=(x + 5, y - 5), font_size="9px"))

    drawing.save()

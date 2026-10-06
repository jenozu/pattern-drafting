import svgwrite
from geometry import cm_to_mm

def _mm(point, x_offset_cm=0.0, y_offset_cm=0.0):
    return (cm_to_mm(point[0] + x_offset_cm), cm_to_mm(point[1] + y_offset_cm))

def _path_for_segments(drawing, segments, x_offset_cm=0.0, y_offset_cm=0.0):
    first = segments[0]["start"]
    sx, sy = _mm(first, x_offset_cm, y_offset_cm)
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

def _piece_width(piece):
    xs = [p[0] for p in piece["points"].values()]
    return max(xs) - min(xs)

def export_svg(draft, filename="pants_block.svg", debug=True):
    front = draft["pieces"]["front"]
    back = draft["pieces"]["back"]
    margin_cm = 2.0
    gap_cm = 6.0
    front_offset = margin_cm - min(p[0] for p in front["points"].values())
    back_offset = front_offset + _piece_width(front) + gap_cm - min(p[0] for p in back["points"].values())
    total_width_cm = back_offset + max(p[0] for p in back["points"].values()) + margin_cm
    total_height_cm = draft["guides"]["height"] + margin_cm * 2

    drawing = svgwrite.Drawing(
        filename,
        size=(f"{cm_to_mm(total_width_cm)}mm", f"{cm_to_mm(total_height_cm)}mm"),
        viewBox=f"0 0 {cm_to_mm(total_width_cm)} {cm_to_mm(total_height_cm)}",
    )
    drawing.add(drawing.rect(insert=(0, 0), size=("100%", "100%"), fill="white"))

    for piece_name, piece, xoff in (("front", front, front_offset), ("back", back, back_offset)):
        yoff = margin_cm
        drawing.add(_path_for_segments(drawing, piece["segments"], xoff, yoff))

        hem_pts = [piece["points"]["side_hem"], piece["points"]["inseam_hem"]]
        crease_x = (hem_pts[0][0] + hem_pts[1][0]) / 2.0
        gx = cm_to_mm(crease_x + xoff)
        drawing.add(drawing.line(
            start=(gx, cm_to_mm(yoff + 8)),
            end=(gx, cm_to_mm(yoff + draft["guides"]["height"] - 4)),
            stroke="gray", stroke_dasharray="8,6"
        ))
        drawing.add(drawing.text(piece_name.upper(), insert=(cm_to_mm(xoff + 1), cm_to_mm(yoff + 5)), font_size="18px"))

        if debug:
            for name, point in piece["points"].items():
                x, y = _mm(point, xoff, yoff)
                drawing.add(drawing.circle(center=(x, y), r=3, fill="red"))
                drawing.add(drawing.text(name, insert=(x + 5, y - 5), font_size="9px"))

    drawing.save()

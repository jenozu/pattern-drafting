import svgwrite
from geometry import cm_to_mm

def _mm(point, x_offset_cm=0.0, y_offset_cm=0.0):
    return (cm_to_mm(point[0] + x_offset_cm), cm_to_mm(point[1] + y_offset_cm))

def _path_for_segments(drawing, segments, x_offset_cm=0.0, y_offset_cm=0.0):
    sx, sy = _mm(segments[0]["start"], x_offset_cm, y_offset_cm)
    path = drawing.path(
        d=f"M {sx} {sy}",
        fill="none",
        stroke="black",
        stroke_width=2,
        stroke_linejoin="round",
        stroke_linecap="round",
    )
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

def _draw_notch(drawing, point, xoff, yoff):
    x, y = _mm(point, xoff, yoff)
    half = cm_to_mm(0.25)
    drawing.add(
        drawing.line(
            start=(x - half, y),
            end=(x + half, y),
            stroke="black",
            stroke_width=1.5,
        )
    )

def export_svg(draft, filename="pants_block.svg", debug=True):
    front = draft["pieces"]["front"]
    back = draft["pieces"]["back"]
    margin_cm = 2.0
    gap_cm = 6.0
    footer_cm = 7.0

    fminx, fmaxx, fminy, fmaxy = _bounds(front)
    bminx, bmaxx, bminy, bmaxy = _bounds(back)
    front_xoff = margin_cm - fminx
    front_yoff = margin_cm - min(0.0, fminy)
    back_xoff = front_xoff + (fmaxx - fminx) + gap_cm - bminx
    back_yoff = margin_cm - min(0.0, bminy)
    pattern_bottom_cm = max(front_yoff + fmaxy, back_yoff + bmaxy)
    total_width_cm = back_xoff + bmaxx + margin_cm
    total_height_cm = pattern_bottom_cm + footer_cm

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
        grain_top = cm_to_mm(yoff + 7)
        grain_bottom = cm_to_mm(yoff + draft["guides"]["height"] - 4)
        drawing.add(
            drawing.line(
                start=(gx, grain_top),
                end=(gx, grain_bottom),
                stroke="gray",
                stroke_dasharray="8,6",
            )
        )
        drawing.add(
            drawing.text(
                "GRAIN",
                insert=(gx + 4, (grain_top + grain_bottom) / 2),
                font_size="10px",
            )
        )

        piece_min_x = min(p[0] for p in piece["points"].values())
        drawing.add(
            drawing.text(
                piece_name.upper(),
                insert=(cm_to_mm(piece_min_x + xoff), cm_to_mm(yoff + 5)),
                font_size="18px",
                font_weight="bold",
            )
        )

        dart = piece.get("markings", {}).get("dart")
        if dart:
            lx, ly = _mm(dart["left"], xoff, yoff)
            rx, ry = _mm(dart["right"], xoff, yoff)
            tx, ty = _mm(dart["tip"], xoff, yoff)
            drawing.add(drawing.line(start=(lx, ly), end=(tx, ty), stroke="black", stroke_width=1))
            drawing.add(drawing.line(start=(rx, ry), end=(tx, ty), stroke="black", stroke_width=1))

        for point in piece.get("markings", {}).get("notches", {}).values():
            _draw_notch(drawing, point, xoff, yoff)

        if debug:
            minx, maxx, _, _ = _bounds(piece)
            for guide_name in ("y_hip", "y_crotch", "y_knee"):
                y = cm_to_mm(draft["guides"][guide_name] + yoff)
                drawing.add(
                    drawing.line(
                        start=(cm_to_mm(minx + xoff), y),
                        end=(cm_to_mm(maxx + xoff), y),
                        stroke="lightgray",
                        stroke_dasharray="4,4",
                    )
                )
            for name, point in piece["points"].items():
                x, y = _mm(point, xoff, yoff)
                drawing.add(drawing.circle(center=(x, y), r=3, fill="red"))
                drawing.add(drawing.text(name, insert=(x + 5, y - 5), font_size="9px"))

    square_x = cm_to_mm(margin_cm)
    square_y = cm_to_mm(pattern_bottom_cm + 1.0)
    square_size = cm_to_mm(5.0)
    drawing.add(
        drawing.rect(
            insert=(square_x, square_y),
            size=(square_size, square_size),
            fill="none",
            stroke="black",
            stroke_width=1.5,
        )
    )
    drawing.add(
        drawing.text(
            "5 cm calibration square",
            insert=(square_x + square_size + 8, square_y + square_size / 2),
            font_size="11px",
        )
    )
    drawing.add(
        drawing.text(
            "BASE BLOCK - NO SEAM ALLOWANCE",
            insert=(cm_to_mm(10.0), square_y + square_size / 2 + 18),
            font_size="11px",
        )
    )

    drawing.save()

import svgwrite
from geometry import cm_to_mm

def export_svg(draft, filename="pants_block.svg"):
    width_mm = cm_to_mm(draft["guides"]["width"])
    height_mm = cm_to_mm(draft["guides"]["height"])
    drawing = svgwrite.Drawing(filename, size=(f"{width_mm + 200}mm", f"{height_mm + 200}mm"))
    drawing.add(drawing.rect(insert=(0, 0), size=(width_mm, height_mm), fill="none", stroke="black"))

    for key in ("y_hip", "y_crotch", "y_knee", "y_hem"):
        y = cm_to_mm(draft["guides"][key])
        drawing.add(drawing.line(start=(0, y), end=(width_mm, y), stroke="gray"))

    x_split = cm_to_mm(draft["guides"]["x_split"])
    drawing.add(drawing.line(start=(x_split, 0), end=(x_split, height_mm), stroke="gray"))

    for key in ("front_crease_x", "back_crease_x"):
        x = cm_to_mm(draft["guides"][key])
        drawing.add(drawing.line(start=(x, 0), end=(x, height_mm), stroke="blue"))

    for name, (x_cm, y_cm) in draft["points"].items():
        x, y = cm_to_mm(x_cm), cm_to_mm(y_cm)
        drawing.add(drawing.circle(center=(x, y), r=3, fill="red"))
        drawing.add(drawing.text(name, insert=(x + 5, y - 5), font_size="10px"))
    drawing.save()

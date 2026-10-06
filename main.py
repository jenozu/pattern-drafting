from drafting import draft_basic_pants_block
from measurements import DraftConfig, Measurements
from svg_export import export_svg

def ask_float(label: str, default: float | None = None) -> float:
    suffix = f" [{default}]" if default is not None else ""
    raw = input(f"{label} (cm){suffix}: ").strip()
    if not raw and default is not None:
        return default
    return float(raw)

def main():
    m = Measurements(
        waist=ask_float("Waist circumference"),
        hip=ask_float("Hip circumference"),
        waist_to_hip=ask_float("Waist to hip"),
        crotch_depth=ask_float("Crotch depth"),
        waist_to_knee=ask_float("Waist to knee"),
        waist_to_ankle=ask_float("Waist to ankle"),
    )
    cfg = DraftConfig(hem_circ=ask_float("Hem circumference", 46.0))
    export_svg(draft_basic_pants_block(m, cfg), "pants_block.svg")
    print("Wrote pants_block.svg")

if __name__ == "__main__":
    main()

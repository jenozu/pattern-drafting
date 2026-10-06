import argparse
import json
from pathlib import Path

from drafting import draft_basic_pants_block
from measurements import DraftConfig, Measurements
from svg_export import export_svg

MEASUREMENT_KEYS = (
    "waist",
    "hip",
    "waist_to_hip",
    "crotch_depth",
    "waist_to_knee",
    "waist_to_ankle",
)

def ask_float(label: str, default: float | None = None) -> float:
    suffix = f" [{default}]" if default is not None else ""
    raw = input(f"{label} (cm){suffix}: ").strip()
    if not raw and default is not None:
        return default
    return float(raw)

def load_json(path: str):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    missing = [key for key in MEASUREMENT_KEYS if key not in data]
    if missing:
        raise ValueError(f"Missing measurements in JSON: {', '.join(missing)}")
    measurements = Measurements(**{key: float(data[key]) for key in MEASUREMENT_KEYS})
    hem_circ = float(data.get("hem_circ", 46.0))
    return measurements, hem_circ

def interactive_measurements():
    return Measurements(
        waist=ask_float("Waist circumference"),
        hip=ask_float("Hip circumference"),
        waist_to_hip=ask_float("Waist to hip"),
        crotch_depth=ask_float("Crotch depth"),
        waist_to_knee=ask_float("Waist to knee"),
        waist_to_ankle=ask_float("Waist to ankle"),
    ), ask_float("Hem circumference", 46.0)

def report_payload(draft):
    return {
        "guides": draft["guides"],
        "seam_walk": draft["seam_walk"],
        "checks": draft["checks"],
        "status": {
            "seam_allowance_added": False,
            "physical_fit_validation_required": True,
        },
    }

def build_parser():
    parser = argparse.ArgumentParser(description="Draft a basic pants/trouser block.")
    parser.add_argument(
        "--measurements",
        help="Path to a JSON file containing measurements in centimetres.",
    )
    parser.add_argument(
        "--output",
        default="pants_block.svg",
        help="SVG output path (default: pants_block.svg).",
    )
    parser.add_argument(
        "--report",
        help="Optional JSON path for construction/seam-walk diagnostics.",
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Hide debug points and construction guides in the SVG.",
    )
    parser.add_argument(
        "--no-seam-walk",
        action="store_true",
        help="Keep the raw drafted seams without automatic equalization.",
    )
    return parser

def main(argv=None):
    args = build_parser().parse_args(argv)
    if args.measurements:
        measurements, hem_circ = load_json(args.measurements)
    else:
        measurements, hem_circ = interactive_measurements()

    cfg = DraftConfig(
        hem_circ=hem_circ,
        auto_seam_walk=not args.no_seam_walk,
    )
    draft = draft_basic_pants_block(measurements, cfg)
    export_svg(draft, args.output, debug=not args.clean)

    if args.report:
        Path(args.report).write_text(
            json.dumps(report_payload(draft), indent=2),
            encoding="utf-8",
        )

    walk = draft["seam_walk"]
    print(f"Wrote {args.output}")
    print(
        "Seam walk after equalization: "
        f"side={walk['after']['upper_side_difference_cm'] * 10:.2f} mm, "
        f"inseam={walk['after']['upper_inseam_difference_cm'] * 10:.2f} mm"
    )
    if args.report:
        print(f"Wrote {args.report}")

if __name__ == "__main__":
    main()

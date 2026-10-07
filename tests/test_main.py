import json

from main import load_json, main

def test_json_cli_generates_svg_and_report(tmp_path):
    source = tmp_path / "measurements.json"
    output = tmp_path / "block.svg"
    report = tmp_path / "report.json"
    source.write_text(
        json.dumps(
            {
                "waist": 74,
                "hip": 96,
                "waist_to_hip": 20,
                "crotch_depth": 26,
                "waist_to_knee": 60,
                "waist_to_ankle": 104,
                "hem_circ": 46,
            }
        )
    )

    main([
        "--measurements", str(source),
        "--output", str(output),
        "--report", str(report),
        "--clean",
    ])

    assert output.exists()
    assert report.exists()
    payload = json.loads(report.read_text())
    assert payload["status"]["seam_allowance_added"] is False
    assert abs(payload["seam_walk"]["after"]["upper_side_difference_cm"]) <= 0.75
    assert payload["seam_walk"]["after"]["upper_side_residual_ease_cm"] <= 0.75

def test_load_json_requires_measurement_keys(tmp_path):
    source = tmp_path / "bad.json"
    source.write_text('{"waist": 74}')
    try:
        load_json(str(source))
    except ValueError as exc:
        assert "Missing measurements" in str(exc)
    else:
        raise AssertionError("Expected ValueError")

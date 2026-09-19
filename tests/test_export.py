"""
NOTE on scope: app/storage/export.py currently exports a single
photo's metadata dict (the dict returned by core.image.load_image) --
it has not yet been wired into the class-based ClassRecord /
ClassStudentEntry / ClassPhotoEntry model. There is no class-level
JSON/CSV export function to test yet, so these tests cover the
export pipeline as it's actually implemented today.
"""

import csv
import json
from pathlib import Path

from app.storage.export import build_export_data, export_to_csv, export_to_json


def make_image_data(**overrides):

    data = {
        "path": Path("photo.jpg"),
        "format": "JPEG",
        "file_size_mb": 2.34567,
        "size": (1920, 1080),
        "mode": "RGB",
        "make": "Canon",
        "model": "EOS R5",
        "lens_model": "RF 24-70mm",
        "iso": 400,
        "fnum": 2.8,
        "exposure_time": "1/125",
        "focal": 50.0,
        "date": "2024:01:01 12:00:00",
        "flash": "Off",
        "white_balance": "Auto",
    }

    data.update(overrides)

    return data


class TestBuildExportData:

    def test_includes_the_expected_fields(self):

        exported = build_export_data(make_image_data())

        assert exported["filename"] == "photo.jpg"
        assert exported["format"] == "JPEG"
        assert exported["width"] == 1920
        assert exported["height"] == 1080
        assert exported["color_mode"] == "RGB"
        assert exported["make"] == "Canon"
        assert exported["model"] == "EOS R5"
        assert exported["iso"] == "400"
        assert exported["aperture"] == "2.8"
        assert exported["shutter_speed"] == "1/125"
        assert exported["focal_length"] == "50"

    def test_file_size_is_rounded_to_two_decimal_places(self):

        exported = build_export_data(make_image_data(file_size_mb=2.34567))

        assert exported["file_size_mb"] == 2.35

    def test_missing_exif_fields_render_as_the_placeholder(self):

        exported = build_export_data(make_image_data(make=None, iso=None))

        assert exported["make"] == "—"
        assert exported["iso"] == "—"

    def test_does_not_mutate_the_input_data(self):

        data = make_image_data()
        original = dict(data)

        build_export_data(data)

        assert data == original


class TestExportToJson:

    def test_writes_valid_json_with_the_expected_values(self, tmp_path):

        data = make_image_data()
        output_path = tmp_path / "export.json"

        export_to_json(data, output_path)

        with open(output_path, encoding="utf-8") as f:
            exported = json.load(f)

        assert exported["filename"] == "photo.jpg"
        assert exported["model"] == "EOS R5"
        assert exported["iso"] == "400"

    def test_does_not_mutate_the_source_data(self, tmp_path):

        data = make_image_data()
        original = dict(data)

        export_to_json(data, tmp_path / "export.json")

        assert data == original

    def test_writes_to_the_given_temporary_path_only(self, tmp_path):

        data = make_image_data()
        output_path = tmp_path / "nested" / "export.json"
        output_path.parent.mkdir()

        export_to_json(data, output_path)

        assert output_path.exists()


class TestExportToCsv:

    def test_writes_a_header_row_and_one_data_row(self, tmp_path):

        data = make_image_data()
        output_path = tmp_path / "export.csv"

        export_to_csv(data, output_path)

        with open(output_path, encoding="utf-8", newline="") as f:
            rows = list(csv.reader(f))

        assert len(rows) == 2  # header + one data row

        header, values = rows
        exported = dict(zip(header, values))

        assert exported["filename"] == "photo.jpg"
        assert exported["make"] == "Canon"

    def test_header_matches_build_export_data_keys_exactly(self, tmp_path):

        data = make_image_data()
        output_path = tmp_path / "export.csv"

        export_to_csv(data, output_path)

        with open(output_path, encoding="utf-8", newline="") as f:
            header = next(csv.reader(f))

        assert header == list(build_export_data(data).keys())

    def test_missing_fields_are_exported_as_the_placeholder_in_csv_too(self, tmp_path):

        data = make_image_data(lens_model=None, white_balance=None)
        output_path = tmp_path / "export.csv"

        export_to_csv(data, output_path)

        with open(output_path, encoding="utf-8", newline="") as f:
            rows = list(csv.reader(f))

        exported = dict(zip(rows[0], rows[1]))

        assert exported["lens_model"] == "—"
        assert exported["white_balance"] == "—"

    def test_does_not_mutate_the_source_data(self, tmp_path):

        data = make_image_data()
        original = dict(data)

        export_to_csv(data, tmp_path / "export.csv")

        assert data == original

import csv
import json

from app.core.converters import exif_value


def build_export_data(data):
    return {
        "filename": data["path"].name,
        "format": data["format"],
        "file_size_mb": round(data["file_size_mb"], 2),
        "width": data["size"][0],
        "height": data["size"][1],
        "color_mode": data["mode"],
        "make": exif_value(data["make"]),
        "model": exif_value(data["model"]),
        "lens_model": exif_value(data["lens_model"]),
        "iso": exif_value(data["iso"]),
        "aperture": exif_value(data["fnum"]),
        "shutter_speed": str(exif_value(data["exposure_time"])),
        "focal_length": exif_value(data["focal"]),
        "date_taken": exif_value(data["date"]),
        "flash": exif_value(data["flash"]),
        "white_balance": exif_value(data["white_balance"]),
    }


def export_to_json(data, path):
    export_data = build_export_data(data)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(export_data, f, indent=2, ensure_ascii=False)


def export_to_csv(data, path):
    export_data = build_export_data(data)

    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(export_data.keys())
        writer.writerow(export_data.values())
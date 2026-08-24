from PIL import Image, UnidentifiedImageError
from pathlib import Path
from fractions import Fraction
import piexif
import json
import csv


def load_image(loc):
    """
    Load image and return image-related information.
    """

    loc = loc.strip().strip('"').strip("'")

    path = Path(loc)

    # Open image with Pillow
    image = Image.open(path)

    # -----------------------------------------
    # BASIC IMAGE INFORMATION
    # -----------------------------------------

    image_format = image.format
    size = image.size
    mode = image.mode

    # -----------------------------------------
    # FILE SIZE
    # -----------------------------------------

    file_size = path.stat().st_size
    file_size_mb = file_size / (1024 ** 2)

    # -----------------------------------------
    # EXIF
    # -----------------------------------------

    try:
        exif_dict = piexif.load(str(path))

    except (piexif.InvalidImageDataError, ValueError):
        exif_dict = {}

    # -----------------------------------------
    # EXIF SECTIONS
    # -----------------------------------------

    zeroth_ifd = exif_dict.get("0th", {})
    exif_ifd = exif_dict.get("Exif", {})

    # -----------------------------------------
    # BASIC CAMERA INFORMATION
    # -----------------------------------------

    make = zeroth_ifd.get(piexif.ImageIFD.Make)
    model = zeroth_ifd.get(piexif.ImageIFD.Model)
    lens_model = exif_ifd.get(piexif.ExifIFD.LensModel)

    # -----------------------------------------
    # CAMERA SETTINGS
    # -----------------------------------------

    focal = exif_ifd.get(piexif.ExifIFD.FocalLength)
    fnum = exif_ifd.get(piexif.ExifIFD.FNumber)
    exposure_time = exif_ifd.get(piexif.ExifIFD.ExposureTime)
    iso = exif_ifd.get(piexif.ExifIFD.ISOSpeedRatings)
    flash = exif_ifd.get(piexif.ExifIFD.Flash)
    white_balance = exif_ifd.get(piexif.ExifIFD.WhiteBalance)

    # -----------------------------------------
    # DATE
    # -----------------------------------------

    date = exif_ifd.get(piexif.ExifIFD.DateTimeOriginal)

    # If DateTimeOriginal doesn't exist,
    # try normal DateTime from 0th IFD
    if date is None:
        date = zeroth_ifd.get(piexif.ImageIFD.DateTime)

    # -----------------------------------------
    # CONVERT VALUES
    # -----------------------------------------

    make = decode_exif_value(make)
    model = decode_exif_value(model)
    lens_model = decode_exif_value(lens_model)
    date = decode_exif_value(date)

    if fnum:
        fnum = rational_to_float(fnum)

    if focal:
        focal = rational_to_float(focal)

    if exposure_time:
        exposure_time = rational_to_fraction(exposure_time)

    if iso:
        iso = decode_exif_value(iso)

    if flash:
        flash = decode_exif_value(flash)

    if white_balance:
        white_balance = decode_exif_value(white_balance)

    # -----------------------------------------
    # RETURN DATA
    # -----------------------------------------

    return {
        "image": image,
        "path": path,
        "format": image_format,
        "size": size,
        "mode": mode,
        "file_size_mb": file_size_mb,

        # Camera
        "make": make,
        "model": model,
        "lens_model": lens_model,

        # Settings
        "focal": focal,
        "fnum": fnum,
        "exposure_time": exposure_time,
        "iso": iso,
        "flash": flash,
        "white_balance": white_balance,

        # Date
        "date": date,

        # Raw EXIF
        "exif": exif_dict
    }


# -----------------------------------------
# EXIF VALUE HANDLING
# -----------------------------------------

def decode_exif_value(value):
    """
    Convert EXIF bytes into normal Python strings.
    """

    if value is None:
        return None

    if isinstance(value, bytes):
        try:
            return value.decode("utf-8").strip("\x00")
        except UnicodeDecodeError:
            return value.decode("latin-1").strip("\x00")

    return value


def rational_to_float(value):
    """
    Convert EXIF rational value to float.
    """

    if isinstance(value, tuple) and len(value) == 2:

        numerator, denominator = value

        if denominator == 0:
            return None

        return numerator / denominator

    return float(value)


def rational_to_fraction(value):
    """
    Convert EXIF rational value to Fraction.
    """

    if isinstance(value, tuple) and len(value) == 2:

        numerator, denominator = value

        if denominator == 0:
            return None

        return Fraction(numerator, denominator)

    return Fraction(value)


def exif_value(value):
    """
    Display 'Not available' when EXIF data is missing.
    """

    if value is None:
        return "Not available"

    return value


# -----------------------------------------
# RECENT FILES
# -----------------------------------------

RECENT_FILES_PATH = Path(__file__).parent / "recent_files.json"
MAX_RECENT_FILES = 5


def load_recent_files():
    """
    Load the list of recently opened image paths from disk.
    """

    if not RECENT_FILES_PATH.exists():
        return []

    try:
        with open(RECENT_FILES_PATH, "r", encoding="utf-8") as f:
            return json.load(f)

    except (json.JSONDecodeError, OSError):
        return []


def add_recent_file(path):
    """
    Add a path to the recent files list and persist it to disk.
    """

    recent = load_recent_files()

    path = str(path)

    if path in recent:
        recent.remove(path)

    recent.insert(0, path)
    recent = recent[:MAX_RECENT_FILES]

    try:
        with open(RECENT_FILES_PATH, "w", encoding="utf-8") as f:
            json.dump(recent, f, indent=2)

    except OSError:
        pass

    return recent


# -----------------------------------------
# HISTOGRAM
# -----------------------------------------

def get_histogram(image):
    """
    Return per-channel (R, G, B) histogram values (256 bins each).
    """

    rgb_image = image.convert("RGB")

    r, g, b = rgb_image.split()

    return {
        "r": r.histogram(),
        "g": g.histogram(),
        "b": b.histogram()
    }


# -----------------------------------------
# EXPORT
# -----------------------------------------

def build_export_data(data):
    """
    Build a flat, serializable dict of image + EXIF info for export.
    """

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
    """
    Export image + EXIF info to a JSON file.
    """

    export_data = build_export_data(data)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(export_data, f, indent=2, ensure_ascii=False)


def export_to_csv(data, path):
    """
    Export image + EXIF info to a CSV file.
    """

    export_data = build_export_data(data)

    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(export_data.keys())
        writer.writerow(export_data.values())


# -----------------------------------------
# DISPLAY IMAGE INFORMATION
# -----------------------------------------

def display_info(data):

    print("\n==== IMAGE INFORMATION ====")

    print(f"Filename   : {data['path'].name}")
    print(f"Format     : {data['format']}")
    print(f"Size       : {data['file_size_mb']:.2f} MB")
    print(f"Width      : {data['size'][0]} PX")
    print(f"Height     : {data['size'][1]} PX")
    print(f"Color mode : {data['mode']}")


# -----------------------------------------
# DISPLAY EXIF INFORMATION
# -----------------------------------------

def display_exif(data):

    print("\n==== EXIF INFORMATION ====")

    print(f"Make          : {exif_value(data['make'])}")
    print(f"Model         : {exif_value(data['model'])}")
    print(f"Lens Model    : {exif_value(data['lens_model'])}")
    print(f"ISO           : {exif_value(data['iso'])}")
    print(f"Aperture      : {exif_value(data['fnum'])}")
    print(f"Shutter Speed : {exif_value(data['exposure_time'])}")
    print(f"Focal Length  : {exif_value(data['focal'])}")
    print(f"Date Taken    : {exif_value(data['date'])}")
    print(f"Flash         : {exif_value(data['flash'])}")
    print(f"White Balance : {exif_value(data['white_balance'])}")


# -----------------------------------------
# TERMINAL VERSION
# -----------------------------------------

def terminal_mode():

    print("HI, this is a simple terminal image metadata")

    # -----------------------------------------
    # INPUT ERROR HANDLING
    # -----------------------------------------

    while True:

        try:

            loc = input("Enter your image path: ").strip()

            data = load_image(loc)

            break

        except FileNotFoundError:

            print("File not found!")

        except UnidentifiedImageError:

            print("This file is not a valid image!")

        except PermissionError:

            print("Permission denied!")

        except OSError:

            print("Could not open this file!")

    # -----------------------------------------
    # MENU
    # -----------------------------------------

    while True:

        print("\n==== MENU ====")
        print("1. Display image info")
        print("2. Display camera info")
        print("3. Exit")

        choice = input("Enter a number: ").strip()

        if choice == "1":

            display_info(data)

        elif choice == "2":

            display_exif(data)

        elif choice == "3":

            print("Goodbye!")

            break

        else:

            print("Invalid choice!")


# -----------------------------------------
# PROGRAM START
# -----------------------------------------

if __name__ == "__main__":
    terminal_mode()
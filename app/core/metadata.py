import piexif

from .converters import (
    decode_exif_value,
    rational_to_float,
    rational_to_fraction,
)


def extract_metadata(path):
    """
    Extract camera and EXIF metadata from an image.
    """

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
    # RETURN METADATA
    # -----------------------------------------

    return {
        "make": make,
        "model": model,
        "lens_model": lens_model,

        "focal": focal,
        "fnum": fnum,
        "exposure_time": exposure_time,
        "iso": iso,
        "flash": flash,
        "white_balance": white_balance,

        "date": date,

        # Keep raw EXIF data
        "exif": exif_dict,
    }
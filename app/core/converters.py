# -----------------------------------------------------------------
# NOTE: decode_exif_value / rational_to_float / rational_to_fraction /
# exif_value already existed in your project (metadata.py and
# metadata_panel.py both import them). I don't have your original
# file, so I rebuilt them here to match how they're used elsewhere.
# Compare against your real converters.py and keep whichever body
# you already had for these four — only the functions below
# "RULE ENGINE CONVERSIONS" are actually new.
# -----------------------------------------------------------------

def decode_exif_value(value):
    """
    Normalize a raw EXIF value into a clean Python value.

    piexif returns text fields as bytes and numbers as-is. This just
    strips/decodes bytes so the rest of the app never deals with them.
    """

    if value is None:
        return None

    if isinstance(value, bytes):
        return value.decode(errors="ignore").strip("\x00").strip()

    return value


def rational_to_float(rational):
    """
    Convert an EXIF rational (numerator, denominator) into a float.
    Used for Aperture (FNumber) and Focal Length.
    """

    if not rational:
        return None

    numerator, denominator = rational

    if denominator == 0:
        return None

    return numerator / denominator


def rational_to_fraction(rational):
    """
    Convert an EXIF rational into a human-readable string, e.g.
    (1, 125) -> "1/125". Used for Shutter Speed display.
    """

    if not rational:
        return None

    numerator, denominator = rational

    if denominator == 0:
        return None

    if numerator >= denominator:
        # 1 second or slower: show as a decimal instead of a fraction
        return f"{numerator / denominator:g}s"

    return f"{numerator}/{denominator}"


def exif_value(value):
    """
    Format any metadata value for display in the GUI.
    """

    if value is None or value == "":
        return "—"

    if isinstance(value, float):
        return f"{value:g}"

    return str(value)


# -----------------------------------------------------------------
# RULE ENGINE CONVERSIONS (spec section 7)
#
# The Rule Engine needs plain numbers to compare against a
# Minimum/Maximum range. Most factors are already numeric by the
# time they leave metadata.py (ISO, Aperture, Focal Length), but
# Shutter Speed is stored as a display string ("1/125", "2s") and
# needs converting back to seconds first.
# -----------------------------------------------------------------

def shutter_speed_to_seconds(value):
    """
    Convert a shutter speed value as stored by metadata.py
    (e.g. "1/125" or "2s") into a float number of seconds.

    Returns None if the value can't be parsed.
    """

    if value is None:
        return None

    text = str(value).strip()

    if text.endswith("s"):
        try:
            return float(text[:-1])
        except ValueError:
            return None

    if "/" in text:
        numerator_text, _, denominator_text = text.partition("/")

        try:
            numerator = float(numerator_text)
            denominator = float(denominator_text)
        except ValueError:
            return None

        if denominator == 0:
            return None

        return numerator / denominator

    try:
        return float(text)
    except ValueError:
        return None


def to_comparable(factor, raw_value):
    """
    Convert a raw metadata value into a number the Rule Engine can
    compare against a Rule's Minimum/Maximum.

    `factor` is one of the keys defined in rules.FACTORS
    (e.g. "iso", "aperture", "shutter_speed", "focal_length").
    """

    if raw_value is None:
        return None

    if factor == "shutter_speed":
        return shutter_speed_to_seconds(raw_value)

    # ISO, Aperture and Focal Length are already plain numbers
    # by the time metadata.py hands them over.
    try:
        return float(raw_value)
    except (TypeError, ValueError):
        return None

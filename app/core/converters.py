from fractions import Fraction


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
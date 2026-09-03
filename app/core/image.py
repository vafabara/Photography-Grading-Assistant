from pathlib import Path
from PIL import Image

from .metadata import extract_metadata


def load_image(loc):
    """
    Load an image and return image-related information
    together with its EXIF metadata.
    """

    loc = loc.strip().strip('"').strip("'")

    path = Path(loc)

    # -----------------------------------------
    # OPEN IMAGE
    # -----------------------------------------

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
    # EXIF METADATA
    # -----------------------------------------

    metadata = extract_metadata(path)

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

        # EXIF metadata
        **metadata,
    }
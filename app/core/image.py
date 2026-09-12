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


# -----------------------------------------------------------------
# STUDENT PHOTO DISCOVERY (Select Folder, and now also Select
# Files -- new feature: single/multiple individual image selection
# so a one-photo student doesn't need a whole folder just for one
# image). Both entry points share the same extension/count/size
# limits so neither path is more permissive than the other.
# -----------------------------------------------------------------

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tiff"}

MAX_IMAGES_PER_STUDENT = 20
MAX_FOLDER_SIZE_MB = 100


class FolderValidationError(ValueError):
    """Raised when a student's photo folder/selection fails validation."""


def discover_images(folder_path):
    """
    Return every valid image file directly inside `folder_path`,
    sorted by filename. Only files whose extension is in
    IMAGE_EXTENSIONS are counted -- anything else (a stray .txt,
    .psd, folder, etc.) is ignored rather than crashing the scan.
    """

    folder_path = Path(folder_path)

    return sorted(
        path for path in folder_path.iterdir()
        if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS
    )


def scan_student_folder(folder_path):
    """
    Discover and validate the images inside one student's folder.

    Returns the list of image Paths on success.

    Raises FolderValidationError (with a message ready to show
    directly in the GUI) if:
      - the folder has no supported images at all
      - the folder has more than MAX_IMAGES_PER_STUDENT images
      - the images inside total more than MAX_FOLDER_SIZE_MB

    This runs before any Rule Engine / Teacher Grading processing
    starts, so a bad folder never gets partway into the review flow.
    """

    images = discover_images(folder_path)

    if not images:
        raise FolderValidationError(
            "This folder does not contain any supported image files."
        )

    if len(images) > MAX_IMAGES_PER_STUDENT:
        raise FolderValidationError(
            f"This folder contains more than {MAX_IMAGES_PER_STUDENT} images."
        )

    total_size_mb = sum(
        path.stat().st_size for path in images
    ) / (1024 ** 2)

    if total_size_mb > MAX_FOLDER_SIZE_MB:
        raise FolderValidationError(
            f"The total image size exceeds the {MAX_FOLDER_SIZE_MB} MB limit."
        )

    return images


def validate_selected_files(file_paths):
    """
    Validate a list of individually-selected image files (new
    feature: Select Files, as an alternative to Select Folder).
    Enforces the same limits as scan_student_folder so neither
    selection path is more permissive than the other.

    Returns the sorted list of image Paths on success. Raises
    FolderValidationError on the same conditions scan_student_folder
    does (no valid images, too many images, total size too large),
    plus rejecting any file whose extension isn't supported.
    """

    paths = [Path(file_path) for file_path in file_paths]

    if not paths:
        raise FolderValidationError(
            "Please select at least one image file."
        )

    unsupported = [
        path for path in paths
        if path.suffix.lower() not in IMAGE_EXTENSIONS
    ]

    if unsupported:
        raise FolderValidationError(
            "One or more selected files are not supported image files."
        )

    if len(paths) > MAX_IMAGES_PER_STUDENT:
        raise FolderValidationError(
            f"You can select at most {MAX_IMAGES_PER_STUDENT} images."
        )

    total_size_mb = sum(
        path.stat().st_size for path in paths
    ) / (1024 ** 2)

    if total_size_mb > MAX_FOLDER_SIZE_MB:
        raise FolderValidationError(
            f"The total image size exceeds the {MAX_FOLDER_SIZE_MB} MB limit."
        )

    return sorted(paths)
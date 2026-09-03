import customtkinter as ctk

from ..core.converters import exif_value
from .widgets import create_info_label


class MetadataPanel:

    def __init__(self, parent):

        self.frame = ctk.CTkScrollableFrame(
            parent,
            corner_radius=12
        )

        self.frame.pack(
            side="right",
            fill="both",
            expand=True,
            padx=(10, 0)
        )

        self.create_file_section()
        self.create_camera_section()

    def create_file_section(self):

        self.file_title = ctk.CTkLabel(
            self.frame,
            text="🗂️  File Information",
            font=ctk.CTkFont(
                size=20,
                weight="bold"
            )
        )

        self.file_title.pack(
            anchor="w",
            padx=20,
            pady=(20, 15)
        )

        self.filename_label = create_info_label(
            self.frame,
            "Filename: —"
        )

        self.format_label = create_info_label(
            self.frame,
            "Format: —"
        )

        self.filesize_label = create_info_label(
            self.frame,
            "File Size: —"
        )

        self.width_label = create_info_label(
            self.frame,
            "Width: —"
        )

        self.height_label = create_info_label(
            self.frame,
            "Height: —"
        )

        self.mode_label = create_info_label(
            self.frame,
            "Color Mode: —"
        )

        self.separator = ctk.CTkFrame(
            self.frame,
            height=2,
            fg_color="gray30"
        )

        self.separator.pack(
            fill="x",
            padx=20,
            pady=20
        )

    def create_camera_section(self):

        self.camera_title = ctk.CTkLabel(
            self.frame,
            text="📸  Camera Information",
            font=ctk.CTkFont(
                size=20,
                weight="bold"
            )
        )

        self.camera_title.pack(
            anchor="w",
            padx=20,
            pady=(0, 15)
        )

        self.make_label = create_info_label(
            self.frame,
            "Make: —"
        )

        self.model_label = create_info_label(
            self.frame,
            "Model: —"
        )

        self.lens_model_label = create_info_label(
            self.frame,
            "Lens Model: —"
        )

        self.iso_label = create_info_label(
            self.frame,
            "ISO: —"
        )

        self.aperture_label = create_info_label(
            self.frame,
            "Aperture: —"
        )

        self.shutter_label = create_info_label(
            self.frame,
            "Shutter Speed: —"
        )

        self.focal_label = create_info_label(
            self.frame,
            "Focal Length: —"
        )

        self.date_label = create_info_label(
            self.frame,
            "Date Taken: —"
        )

        self.flash_label = create_info_label(
            self.frame,
            "Flash: —"
        )

        self.white_balance_label = create_info_label(
            self.frame,
            "White Balance: —"
        )

    def update(self, data):

        size = data["size"]

        self.filename_label.configure(
            text=f"Filename: {data['path'].name}"
        )

        self.format_label.configure(
            text=f"Format: {data['format']}"
        )

        self.filesize_label.configure(
            text=f"File Size: {data['file_size_mb']:.2f} MB"
        )

        self.width_label.configure(
            text=f"Width: {size[0]} PX"
        )

        self.height_label.configure(
            text=f"Height: {size[1]} PX"
        )

        self.mode_label.configure(
            text=f"Color Mode: {data['mode']}"
        )

        self.make_label.configure(
            text=f"Make: {exif_value(data['make'])}"
        )

        self.model_label.configure(
            text=f"Model: {exif_value(data['model'])}"
        )

        self.lens_model_label.configure(
            text=f"Lens Model: {exif_value(data['lens_model'])}"
        )

        self.iso_label.configure(
            text=f"ISO: {exif_value(data['iso'])}"
        )

        self.aperture_label.configure(
            text=f"Aperture: {exif_value(data['fnum'])}"
        )

        self.shutter_label.configure(
            text=f"Shutter Speed: {exif_value(data['exposure_time'])}"
        )

        self.focal_label.configure(
            text=f"Focal Length: {exif_value(data['focal'])}"
        )

        self.date_label.configure(
            text=f"Date Taken: {exif_value(data['date'])}"
        )

        self.flash_label.configure(
            text=f"Flash: {exif_value(data['flash'])}"
        )

        self.white_balance_label.configure(
            text=f"White Balance: {exif_value(data['white_balance'])}"
        )
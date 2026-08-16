import customtkinter as ctk
from tkinter import filedialog
from PIL import ImageTk

import main


class App(ctk.CTk):

    def __init__(self):
        super().__init__()

        # Window
        self.title("Image Metadata")
        self.geometry("1050x700")
        self.minsize(900, 600)

        # Appearance
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("green")

        # Current image
        self.current_image = None
        self.image_tk = None

        # Main frame
        self.main_frame = ctk.CTkFrame(
            self,
            corner_radius=15
        )

        self.main_frame.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=20
        )

        self.create_header()
        self.create_content()
        self.create_bottom_bar()

    # HEADER
    def create_header(self):

        self.header = ctk.CTkFrame(
            self.main_frame,
            fg_color="transparent"
        )

        self.header.pack(
            fill="x",
            padx=25,
            pady=(20, 10)
        )

        self.title_label = ctk.CTkLabel(
            self.header,
            text="📷  Image Metadata",
            font=ctk.CTkFont(
                size=28,
                weight="bold"
            ),
            text_color="#7CFFB2"
        )

        self.title_label.pack(
            side="left"
        )

        self.subtitle_label = ctk.CTkLabel(
            self.header,
            text="View image information and EXIF metadata",
            text_color="gray60",
            font=ctk.CTkFont(
                size=13
            )
        )

        self.subtitle_label.pack(
            side="left",
            padx=15
        )

    # CONTENT
    def create_content(self):

        self.content = ctk.CTkFrame(
            self.main_frame,
            fg_color="transparent"
        )

        self.content.pack(
            fill="both",
            expand=True,
            padx=25,
            pady=10
        )

        # Left side
        self.create_preview()

        # Right side
        self.create_information()

    # IMAGE PREVIEW
    def create_preview(self):

        self.preview_frame = ctk.CTkFrame(
            self.content,
            corner_radius=12
        )

        self.preview_frame.pack(
            side="left",
            fill="both",
            expand=True,
            padx=(0, 10)
        )

        self.preview_label = ctk.CTkLabel(
            self.preview_frame,
            text="🖼️\nNo Image Selected",
            text_color="#7CFFB2",
            font=ctk.CTkFont(
                size=20
            )
        )

        self.preview_label.place(
            relx=0.5,
            rely=0.5,
            anchor="center"
        )

    # INFORMATION
    def create_information(self):

        self.info_frame = ctk.CTkScrollableFrame(
            self.content,
            corner_radius=12
        )

        self.info_frame.pack(
            side="right",
            fill="both",
            expand=True,
            padx=(10, 0)
        )

        # File information
        self.file_title = ctk.CTkLabel(
            self.info_frame,
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

        self.filename_label = self.create_info_label(
            "Filename: —"
        )

        self.format_label = self.create_info_label(
            "Format: —"
        )

        self.filesize_label = self.create_info_label(
            "File Size: —"
        )

        self.width_label = self.create_info_label(
            "Width: —"
        )

        self.height_label = self.create_info_label(
            "Height: —"
        )

        self.mode_label = self.create_info_label(
            "Color Mode: —"
        )

        # Separator
        self.separator = ctk.CTkFrame(
            self.info_frame,
            height=2,
            fg_color="gray30"
        )

        self.separator.pack(
            fill="x",
            padx=20,
            pady=20
        )

        # Camera information
        self.camera_title = ctk.CTkLabel(
            self.info_frame,
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

        self.make_label = self.create_info_label(
            "Make: —"
        )

        self.model_label = self.create_info_label(
            "Model: —"
        )

        self.lens_model_label = self.create_info_label(
            "Lens Model: —"
        )

        self.iso_label = self.create_info_label(
            "ISO: —"
        )

        self.aperture_label = self.create_info_label(
            "Aperture: —"
        )

        self.shutter_label = self.create_info_label(
            "Shutter Speed: —"
        )

        self.focal_label = self.create_info_label(
            "Focal Length: —"
        )

        self.date_label = self.create_info_label(
            "Date Taken: —"
        )

        self.flash_label = self.create_info_label(
            "Flash: —"
        )

        self.white_balance_label = self.create_info_label(
            "White Balance: —"
        )

    # INFORMATION LABEL
    def create_info_label(self, text):

        label = ctk.CTkLabel(
            self.info_frame,
            text=text,
            font=ctk.CTkFont(
                size=14
            ),
            anchor="w"
        )

        label.pack(
            fill="x",
            padx=20,
            pady=5
        )

        return label

    # BOTTOM BAR
    def create_bottom_bar(self):

        self.bottom_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color="transparent"
        )

        self.bottom_frame.pack(
            fill="x",
            padx=25,
            pady=(10, 20)
        )

        self.open_button = ctk.CTkButton(
            self.bottom_frame,
            text="📂  Open Image",
            width=150,
            height=40,
            fg_color="#1F8F4C",
            hover_color="#27AE60",
            font=ctk.CTkFont(
                size=14,
                weight="bold"
            ),
            command=self.open_image
        )

        self.open_button.pack(
            side="left"
        )

        self.exit_button = ctk.CTkButton(
            self.bottom_frame,
            text="✕  Exit",
            width=100,
            height=40,
            fg_color="transparent",
            hover_color="#123f2c",
            border_color="#2ECC71",
            text_color="#7CFFB2",
            border_width=1,
            command=self.destroy
        )

        self.exit_button.pack(
            side="right"
        )

    # OPEN IMAGE
    def open_image(self):

        file_path = filedialog.askopenfilename(
            title="Select an image",
            filetypes=[
                (
                    "Image files",
                    "*.jpg *.jpeg *.png *.webp *.bmp *.tiff"
                ),
                (
                    "All files",
                    "*.*"
                )
            ]
        )

        if not file_path:
            return

        try:

            data = main.load_image(file_path)

            self.current_image = data["image"]

            self.update_preview()

            self.update_information(data)

        except FileNotFoundError:

            self.show_error("File not found.")

        except main.UnidentifiedImageError:

            self.show_error(
                "This file is not a valid image."
            )

    # -----------------------------------------
    # IMAGE PREVIEW
    # -----------------------------------------

    def update_preview(self):

        image = self.current_image.copy()

        # Thumbnail
        image.thumbnail((500, 500))

        self.image_tk = ImageTk.PhotoImage(image)

        self.preview_label.configure(
            image=self.image_tk,
            text=""
        )

    # UPDATE INFORMATION

    def update_information(self, data):

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

        # EXIF
        self.make_label.configure(
            text=f"Make: {main.exif_value(data['make'])}"
        )

        self.model_label.configure(
            text=f"Model: {main.exif_value(data['model'])}"
        )

        self.lens_model_label.configure(
            text=f"Lens Model: {main.exif_value(data['lens_model'])}"
        )

        self.iso_label.configure(
            text=f"ISO: {main.exif_value(data['iso'])}"
        )

        self.aperture_label.configure(
            text=f"Aperture: {main.exif_value(data['fnum'])}"
        )

        self.shutter_label.configure(
            text=(
                f"Shutter Speed: "
                f"{main.exif_value(data['exposure_time'])}"
            )
        )

        self.focal_label.configure(
            text=f"Focal Length: {main.exif_value(data['focal'])}"
        )

        self.date_label.configure(
            text=f"Date Taken: {main.exif_value(data['date'])}"
        )

        self.flash_label.configure(
            text=f"Flash: {main.exif_value(data['flash'])}"
        )

        self.white_balance_label.configure(
            text=f"White Balance: {main.exif_value(data['white_balance'])}"
        )

    # -----------------------------------------
    # ERROR
    # -----------------------------------------

    def show_error(self, message):

        error_window = ctk.CTkToplevel(self)

        error_window.title("Error")
        error_window.geometry("400x180")

        error_window.resizable(
            False,
            False
        )

        label = ctk.CTkLabel(
            error_window,
            text=message,
            font=ctk.CTkFont(
                size=15
            ),
            wraplength=340
        )

        label.pack(
            pady=(35, 20)
        )

        button = ctk.CTkButton(
            error_window,
            text="OK",
            width=100,
            command=error_window.destroy
        )

        button.pack()


if __name__ == "__main__":

    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("green")

    app = App()
    app.mainloop()
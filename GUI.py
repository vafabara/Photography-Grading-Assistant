import customtkinter as ctk
from tkinter import filedialog, Canvas
from tkinterdnd2 import TkinterDnD, DND_FILES
from PIL import ImageTk
from pathlib import Path

import main


# -----------------------------------------
# ACCENT COLOR PALETTE
# -----------------------------------------

COLOR_PALETTE = {
    "Green":  {"text": "#7CFFB2", "fg": "#1F8F4C", "hover": "#27AE60", "border": "#2ECC71"},
    "Blue":   {"text": "#7CC7FF", "fg": "#1F6F9F", "hover": "#278FCE", "border": "#2E9FE6"},
    "Purple": {"text": "#C79CFF", "fg": "#6C3F9F", "hover": "#8850C7", "border": "#9B5CE6"},
    "Red":    {"text": "#FF9C9C", "fg": "#9F3F3F", "hover": "#C75050", "border": "#E65C5C"},
    "Orange": {"text": "#FFC27C", "fg": "#9F6A1F", "hover": "#C7862A", "border": "#E69633"},
    "Pink":   {"text": "#FF9CD6", "fg": "#9F3F80", "hover": "#C750A0", "border": "#E65CB4"},
    "Teal":   {"text": "#7CFFE9", "fg": "#1F9F8C", "hover": "#27C7AC", "border": "#2EE6C2"},
}


class App(ctk.CTk, TkinterDnD.DnDWrapper):

    def __init__(self):
        super().__init__()

        # Enable drag & drop support on this Tk instance
        self.TkdndVersion = TkinterDnD._require(self)

        # Window
        self.title("Image Metadata")
        self.geometry("1050x700")
        self.minsize(900, 600)

        # Appearance
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("green")

        # Current image
        self.current_image = None
        self.current_data = None
        self.image_tk = None
        self.recent_map = {}
        self.accent_color = "Green"

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

        self.refresh_recent_menu()
        self.apply_accent_color(self.accent_color)

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

        self.settings_button = ctk.CTkButton(
            self.header,
            text="⚙",
            width=40,
            height=40,
            fg_color="transparent",
            hover_color="#123f2c",
            border_width=1,
            font=ctk.CTkFont(
                size=16
            ),
            command=self.open_settings
        )

        self.settings_button.pack(
            side="right"
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

        # Histogram canvas (packed first so it stays at the bottom)
        self.histogram_canvas = Canvas(
            self.preview_frame,
            height=110,
            bg="#1a1a1a",
            highlightthickness=0
        )

        self.histogram_canvas.pack(
            side="bottom",
            fill="x",
            padx=12,
            pady=12
        )

        self.preview_label = ctk.CTkLabel(
            self.preview_frame,
            text="🖼️\nNo Image Selected\n(or drag & drop one here)",
            text_color="#7CFFB2",
            font=ctk.CTkFont(
                size=20
            )
        )

        self.preview_label.pack(
            fill="both",
            expand=True
        )

        # Drag & drop support
        self.preview_frame.drop_target_register(DND_FILES)
        self.preview_frame.dnd_bind("<<Drop>>", self.on_drop)

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

        self.copy_button = ctk.CTkButton(
            self.bottom_frame,
            text="📋  Copy Info",
            width=140,
            height=40,
            fg_color="transparent",
            hover_color="#123f2c",
            border_color="#2ECC71",
            text_color="#7CFFB2",
            border_width=1,
            command=self.copy_info_to_clipboard
        )

        self.copy_button.pack(
            side="left",
            padx=(10, 0)
        )

        self.export_button = ctk.CTkButton(
            self.bottom_frame,
            text="📤  Export",
            width=140,
            height=40,
            fg_color="transparent",
            hover_color="#123f2c",
            border_color="#2ECC71",
            text_color="#7CFFB2",
            border_width=1,
            command=self.export_info
        )

        self.export_button.pack(
            side="left",
            padx=(10, 0)
        )

        self.recent_menu = ctk.CTkOptionMenu(
            self.bottom_frame,
            values=["No recent files"],
            command=self.open_recent,
            width=220
        )

        self.recent_menu.pack(
            side="left",
            padx=(10, 0)
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

        self.load_and_display(file_path)

    # DRAG & DROP
    def on_drop(self, event):

        # Dropped paths with spaces are wrapped in curly braces
        file_path = event.data.strip("{}")

        self.load_and_display(file_path)

    # RECENT FILES
    def refresh_recent_menu(self):

        recent = main.load_recent_files()

        self.recent_map = {
            Path(p).name: p for p in recent
        }

        values = list(self.recent_map.keys()) or ["No recent files"]

        self.recent_menu.configure(values=values)
        self.recent_menu.set(values[0])

    def open_recent(self, name):

        file_path = self.recent_map.get(name)

        if file_path:
            self.load_and_display(file_path)

    # LOAD + DISPLAY (shared by open/drop/recent)
    def load_and_display(self, file_path):

        try:

            data = main.load_image(file_path)

            self.current_image = data["image"]
            self.current_data = data

            self.update_preview()
            self.update_information(data)

            main.add_recent_file(data["path"])
            self.refresh_recent_menu()

        except FileNotFoundError:

            self.show_error("File not found.")

        except main.UnidentifiedImageError:

            self.show_error(
                "This file is not a valid image."
            )

        except OSError:

            self.show_error(
                "Could not open this file."
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

        self.update_histogram(self.current_image)

    # -----------------------------------------
    # HISTOGRAM
    # -----------------------------------------

    def update_histogram(self, image):

        self.histogram_canvas.update_idletasks()

        width = self.histogram_canvas.winfo_width()
        height = self.histogram_canvas.winfo_height()

        if width <= 1 or height <= 1:
            width, height = 400, 110

        self.histogram_canvas.delete("all")

        histogram = main.get_histogram(image)

        colors = {
            "r": "#FF5C5C",
            "g": "#5CFF9C",
            "b": "#5CA8FF"
        }

        for channel, color in colors.items():

            values = histogram[channel]
            max_value = max(values) or 1

            points = []

            for i, value in enumerate(values):
                x = i * (width / 256)
                y = height - (value / max_value) * (height - 4)
                points.append(x)
                points.append(y)

            if len(points) >= 4:
                self.histogram_canvas.create_line(
                    *points,
                    fill=color,
                    width=1,
                    smooth=True
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
    # COPY TO CLIPBOARD
    # -----------------------------------------

    def copy_info_to_clipboard(self):

        if not self.current_data:
            return

        data = self.current_data

        lines = [
            f"Filename: {data['path'].name}",
            f"Format: {data['format']}",
            f"File Size: {data['file_size_mb']:.2f} MB",
            f"Width: {data['size'][0]} PX",
            f"Height: {data['size'][1]} PX",
            f"Color Mode: {data['mode']}",
            f"Make: {main.exif_value(data['make'])}",
            f"Model: {main.exif_value(data['model'])}",
            f"Lens Model: {main.exif_value(data['lens_model'])}",
            f"ISO: {main.exif_value(data['iso'])}",
            f"Aperture: {main.exif_value(data['fnum'])}",
            f"Shutter Speed: {main.exif_value(data['exposure_time'])}",
            f"Focal Length: {main.exif_value(data['focal'])}",
            f"Date Taken: {main.exif_value(data['date'])}",
            f"Flash: {main.exif_value(data['flash'])}",
            f"White Balance: {main.exif_value(data['white_balance'])}",
        ]

        self.clipboard_clear()
        self.clipboard_append("\n".join(lines))
        self.update()

    # -----------------------------------------
    # EXPORT
    # -----------------------------------------

    def export_info(self):

        if not self.current_data:
            self.show_message("Export", "No image loaded to export.")
            return

        self.ask_export_format()

    def ask_export_format(self):

        format_window = ctk.CTkToplevel(self)

        format_window.title("Export Format")
        format_window.geometry("320x170")

        format_window.resizable(
            False,
            False
        )

        label = ctk.CTkLabel(
            format_window,
            text="Choose an export format:",
            font=ctk.CTkFont(
                size=15
            )
        )

        label.pack(
            pady=(30, 20)
        )

        button_frame = ctk.CTkFrame(
            format_window,
            fg_color="transparent"
        )

        button_frame.pack()

        json_button = ctk.CTkButton(
            button_frame,
            text="JSON",
            width=110,
            command=lambda: self.choose_export_location(
                "json",
                format_window
            )
        )

        json_button.pack(
            side="left",
            padx=10
        )

        csv_button = ctk.CTkButton(
            button_frame,
            text="CSV",
            width=110,
            command=lambda: self.choose_export_location(
                "csv",
                format_window
            )
        )

        csv_button.pack(
            side="left",
            padx=10
        )

    def choose_export_location(self, file_format, format_window):

        format_window.destroy()

        default_name = f"{self.current_data['path'].stem}.{file_format}"

        file_path = filedialog.asksaveasfilename(
            title="Save exported file",
            defaultextension=f".{file_format}",
            initialfile=default_name,
            filetypes=[
                (
                    f"{file_format.upper()} files",
                    f"*.{file_format}"
                )
            ]
        )

        if not file_path:
            return

        try:

            if file_format == "json":
                main.export_to_json(self.current_data, file_path)
            else:
                main.export_to_csv(self.current_data, file_path)

            self.show_message(
                "Export",
                "File exported successfully."
            )

        except OSError:

            self.show_message(
                "Error",
                "Could not save the export file."
            )

    # -----------------------------------------
    # SETTINGS
    # -----------------------------------------

    def open_settings(self):

        settings_window = ctk.CTkToplevel(self)

        settings_window.title("Settings")
        settings_window.geometry("320x280")

        settings_window.resizable(
            False,
            False
        )

        appearance_title = ctk.CTkLabel(
            settings_window,
            text="Appearance Mode",
            font=ctk.CTkFont(
                size=14,
                weight="bold"
            )
        )

        appearance_title.pack(
            pady=(25, 10)
        )

        appearance_menu = ctk.CTkSegmentedButton(
            settings_window,
            values=["Light", "Dark"],
            command=self.change_appearance_mode
        )

        appearance_menu.set(ctk.get_appearance_mode())

        appearance_menu.pack(
            pady=(0, 25)
        )

        color_title = ctk.CTkLabel(
            settings_window,
            text="Accent Color",
            font=ctk.CTkFont(
                size=14,
                weight="bold"
            )
        )

        color_title.pack(
            pady=(0, 10)
        )

        color_menu = ctk.CTkOptionMenu(
            settings_window,
            values=list(COLOR_PALETTE.keys()),
            command=self.apply_accent_color,
            width=180
        )

        color_menu.set(self.accent_color)

        color_menu.pack(
            pady=(0, 20)
        )

    def change_appearance_mode(self, mode):

        ctk.set_appearance_mode(mode)

    def apply_accent_color(self, color_name):

        self.accent_color = color_name
        palette = COLOR_PALETTE[color_name]

        self.title_label.configure(
            text_color=palette["text"]
        )

        self.preview_label.configure(
            text_color=palette["text"]
        )

        self.open_button.configure(
            fg_color=palette["fg"],
            hover_color=palette["hover"]
        )

        for button in (
            self.copy_button,
            self.export_button,
            self.settings_button,
            self.exit_button
        ):
            button.configure(
                border_color=palette["border"],
                text_color=palette["text"]
            )

    # -----------------------------------------
    # MESSAGE / ERROR
    # -----------------------------------------

    def show_message(self, title, message):

        message_window = ctk.CTkToplevel(self)

        message_window.title(title)
        message_window.geometry("400x180")

        message_window.resizable(
            False,
            False
        )

        label = ctk.CTkLabel(
            message_window,
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
            message_window,
            text="OK",
            width=100,
            command=message_window.destroy
        )

        button.pack()

    def show_error(self, message):

        self.show_message("Error", message)


if __name__ == "__main__":

    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("green")

    app = App()
    app.mainloop()
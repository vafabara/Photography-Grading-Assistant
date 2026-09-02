import customtkinter as ctk
from tkinter import filedialog, Canvas
from tkinterdnd2 import TkinterDnD, DND_FILES
from PIL import ImageTk
from pathlib import Path

import main


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

        # Student workflow state
        self.student_count = 0
        self.students = []
        self.current_student_index = 0

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

        # Start with the setup workflow instead of the viewer
        self.show_setup_count_screen()

    # -----------------------------------------
    # HELPERS
    # -----------------------------------------

    def clear_main_frame(self):

        for widget in self.main_frame.winfo_children():
            widget.destroy()

    # -----------------------------------------
    # SETUP STEP 1: STUDENT COUNT
    # -----------------------------------------

    def show_setup_count_screen(self):

        self.clear_main_frame()

        frame = ctk.CTkFrame(
            self.main_frame,
            fg_color="transparent"
        )

        frame.pack(expand=True)

        title_label = ctk.CTkLabel(
            frame,
            text="📷  Image Metadata — Class Review Setup",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="#7CFFB2"
        )

        title_label.pack(pady=(0, 25))

        question_label = ctk.CTkLabel(
            frame,
            text="How many students?",
            font=ctk.CTkFont(size=16)
        )

        question_label.pack(pady=(0, 10))

        count_entry = ctk.CTkEntry(
            frame,
            width=200,
            justify="center"
        )

        count_entry.pack(pady=(0, 10))

        error_label = ctk.CTkLabel(
            frame,
            text="",
            text_color="#FF6B6B"
        )

        error_label.pack(pady=(0, 10))

        def on_continue():

            value = count_entry.get().strip()

            if not value.isdigit() or int(value) <= 0:
                error_label.configure(
                    text="Please enter a positive whole number."
                )
                return

            self.student_count = int(value)
            self.show_setup_names_screen()

        continue_button = ctk.CTkButton(
            frame,
            text="Continue",
            width=150,
            height=40,
            fg_color="#1F8F4C",
            hover_color="#27AE60",
            command=on_continue
        )

        continue_button.pack()

    # -----------------------------------------
    # SETUP STEP 2: STUDENT NAMES
    # -----------------------------------------

    def show_setup_names_screen(self):

        self.clear_main_frame()

        container = ctk.CTkFrame(
            self.main_frame,
            fg_color="transparent"
        )

        container.pack(fill="both", expand=True, padx=40, pady=30)

        title_label = ctk.CTkLabel(
            container,
            text="Enter Student Names",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="#7CFFB2"
        )

        title_label.pack(pady=(0, 15))

        scroll_frame = ctk.CTkScrollableFrame(
            container,
            fg_color="transparent"
        )

        scroll_frame.pack(fill="both", expand=True)

        name_entries = []

        for i in range(self.student_count):

            row = ctk.CTkFrame(scroll_frame, fg_color="transparent")
            row.pack(fill="x", pady=5)

            row_label = ctk.CTkLabel(
                row,
                text=f"Student {i + 1} name:",
                width=140,
                anchor="w"
            )

            row_label.pack(side="left", padx=(0, 10))

            entry = ctk.CTkEntry(row, width=250)
            entry.pack(side="left")

            name_entries.append(entry)

        error_label = ctk.CTkLabel(
            container,
            text="",
            text_color="#FF6B6B"
        )

        error_label.pack(pady=(10, 5))

        def on_continue():

            names = [entry.get().strip() for entry in name_entries]

            if any(not name for name in names):
                error_label.configure(
                    text="Please fill in a name for every student."
                )
                return

            self.students = [
                {"name": name, "image_path": None} for name in names
            ]

            self.show_setup_photos_screen()

        continue_button = ctk.CTkButton(
            container,
            text="Continue",
            width=150,
            height=40,
            fg_color="#1F8F4C",
            hover_color="#27AE60",
            command=on_continue
        )

        continue_button.pack(pady=(10, 0))

    # -----------------------------------------
    # SETUP STEP 3: ASSIGN PHOTOS
    # -----------------------------------------

    def show_setup_photos_screen(self):

        self.clear_main_frame()

        container = ctk.CTkFrame(
            self.main_frame,
            fg_color="transparent"
        )

        container.pack(fill="both", expand=True, padx=40, pady=30)

        title_label = ctk.CTkLabel(
            container,
            text="Assign a Photo to Each Student",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="#7CFFB2"
        )

        title_label.pack(pady=(0, 15))

        scroll_frame = ctk.CTkScrollableFrame(
            container,
            fg_color="transparent"
        )

        scroll_frame.pack(fill="both", expand=True)

        self.photo_status_labels = []

        error_label = ctk.CTkLabel(
            container,
            text="",
            text_color="#FF6B6B"
        )

        def select_photo(index):

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

            self.students[index]["image_path"] = file_path

            self.photo_status_labels[index].configure(
                text="✅ Image selected",
                text_color="#7CFFB2"
            )

        for i, student in enumerate(self.students):

            row = ctk.CTkFrame(scroll_frame, fg_color="transparent")
            row.pack(fill="x", pady=8)

            name_label = ctk.CTkLabel(
                row,
                text=f"Student: {student['name']}",
                width=220,
                anchor="w",
                font=ctk.CTkFont(size=14, weight="bold")
            )

            name_label.pack(side="left", padx=(0, 10))

            select_button = ctk.CTkButton(
                row,
                text="Select Photo",
                width=130,
                command=lambda i=i: select_photo(i)
            )

            select_button.pack(side="left", padx=(0, 10))

            status_label = ctk.CTkLabel(
                row,
                text="No image selected",
                text_color="gray60"
            )

            status_label.pack(side="left")

            self.photo_status_labels.append(status_label)

        error_label.pack(pady=(10, 5))

        def on_start_review():

            if any(s["image_path"] is None for s in self.students):
                error_label.configure(
                    text="Please select an image for every student before starting."
                )
                return

            self.start_review()

        start_button = ctk.CTkButton(
            container,
            text="Start Review",
            width=180,
            height=40,
            fg_color="#1F8F4C",
            hover_color="#27AE60",
            command=on_start_review
        )

        start_button.pack(pady=(10, 0))

    # -----------------------------------------
    # REVIEW WORKFLOW
    # -----------------------------------------

    def start_review(self):

        self.current_student_index = 0

        self.clear_main_frame()

        self.create_student_bar()
        self.create_header()
        self.create_content()
        self.create_bottom_bar()

        self.refresh_recent_menu()

        self.load_current_student()

    def create_student_bar(self):

        self.student_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color="transparent"
        )

        self.student_frame.pack(
            fill="x",
            padx=25,
            pady=(20, 0)
        )

        self.student_label = ctk.CTkLabel(
            self.student_frame,
            text="Student: —",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#7CFFB2"
        )

        self.student_label.pack(side="left")

    def load_current_student(self):

        student = self.students[self.current_student_index]

        self.student_label.configure(
            text=f"Student: {student['name']}"
        )

        self.load_and_display(student["image_path"])

    def next_student(self):

        self.current_student_index += 1

        if self.current_student_index >= len(self.students):
            self.show_done_screen()
        else:
            self.load_current_student()

    def show_done_screen(self):

        self.clear_main_frame()

        done_label = ctk.CTkLabel(
            self.main_frame,
            text="Done",
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color="#7CFFB2"
        )

        done_label.pack(expand=True)

    # HEADER
    def create_header(self):

        self.header = ctk.CTkFrame(
            self.main_frame,
            fg_color="transparent"
        )

        self.header.pack(
            fill="x",
            padx=25,
            pady=(10, 10)
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

        self.next_button = ctk.CTkButton(
            self.bottom_frame,
            text="➡️  Next",
            width=120,
            height=40,
            fg_color="#1F8F4C",
            hover_color="#27AE60",
            font=ctk.CTkFont(
                size=14,
                weight="bold"
            ),
            command=self.next_student
        )

        self.next_button.pack(
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

    # LOAD + DISPLAY (shared by open/drop/recent/review)
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
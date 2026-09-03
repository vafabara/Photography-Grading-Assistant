import customtkinter as ctk
from tkinter import filedialog
from tkinterdnd2 import TkinterDnD
from tkinter import TclError

from pathlib import Path
from PIL import UnidentifiedImageError

from ..core.image import load_image
from ..core.converters import exif_value
from ..storage.recent_files import load_recent_files, add_recent_file

from .image_viewer import ImageViewer
from .metadata_panel import MetadataPanel
from .widgets import show_error


class App(ctk.CTk, TkinterDnD.DnDWrapper):

    def __init__(self):
        super().__init__()

        self.TkdndVersion = TkinterDnD._require(self)

        self.title("Image Metadata")
        self.geometry("1050x700")
        self.minsize(900, 600)

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("green")

        # Current image
        self.current_image = None
        self.current_data = None
        self.recent_map = {}

        # Student workflow
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

        self.show_setup_count_screen()

    # -----------------------------------------
    # HELPERS
    # -----------------------------------------

    def clear_main_frame(self):

        for widget in self.main_frame.winfo_children():
            widget.destroy()

    # -----------------------------------------
    # SETUP STEP 1
    # -----------------------------------------

    def show_setup_count_screen(self):

        self.clear_main_frame()

        frame = ctk.CTkFrame(
            self.main_frame,
            fg_color="transparent"
        )

        frame.pack(expand=True)

        ctk.CTkLabel(
            frame,
            text="📷  Image Metadata — Class Review Setup",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="#7CFFB2"
        ).pack(pady=(0, 25))

        ctk.CTkLabel(
            frame,
            text="How many students?",
            font=ctk.CTkFont(size=16)
        ).pack(pady=(0, 10))

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

        ctk.CTkButton(
            frame,
            text="Continue",
            width=150,
            height=40,
            fg_color="#1F8F4C",
            hover_color="#27AE60",
            command=on_continue
        ).pack()

    # -----------------------------------------
    # SETUP STEP 2
    # -----------------------------------------

    def show_setup_names_screen(self):

        self.clear_main_frame()

        container = ctk.CTkFrame(
            self.main_frame,
            fg_color="transparent"
        )

        container.pack(
            fill="both",
            expand=True,
            padx=40,
            pady=30
        )

        ctk.CTkLabel(
            container,
            text="Enter Student Names",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="#7CFFB2"
        ).pack(pady=(0, 15))

        scroll_frame = ctk.CTkScrollableFrame(
            container,
            fg_color="transparent"
        )

        scroll_frame.pack(
            fill="both",
            expand=True
        )

        name_entries = []

        for i in range(self.student_count):

            row = ctk.CTkFrame(
                scroll_frame,
                fg_color="transparent"
            )

            row.pack(
                fill="x",
                pady=5
            )

            ctk.CTkLabel(
                row,
                text=f"Student {i + 1} name:",
                width=140,
                anchor="w"
            ).pack(
                side="left",
                padx=(0, 10)
            )

            entry = ctk.CTkEntry(
                row,
                width=250
            )

            entry.pack(side="left")

            name_entries.append(entry)

        error_label = ctk.CTkLabel(
            container,
            text="",
            text_color="#FF6B6B"
        )

        error_label.pack(pady=(10, 5))

        def on_continue():

            names = [
                entry.get().strip()
                for entry in name_entries
            ]

            if any(not name for name in names):
                error_label.configure(
                    text="Please fill in a name for every student."
                )
                return

            self.students = [
                {
                    "name": name,
                    "image_path": None
                }
                for name in names
            ]

            self.show_setup_photos_screen()

        ctk.CTkButton(
            container,
            text="Continue",
            width=150,
            height=40,
            fg_color="#1F8F4C",
            hover_color="#27AE60",
            command=on_continue
        ).pack(pady=(10, 0))

    # -----------------------------------------
    # SETUP STEP 3
    # -----------------------------------------

    def show_setup_photos_screen(self):

        self.clear_main_frame()

        container = ctk.CTkFrame(
            self.main_frame,
            fg_color="transparent"
        )

        container.pack(
            fill="both",
            expand=True,
            padx=40,
            pady=30
        )

        ctk.CTkLabel(
            container,
            text="Assign a Photo to Each Student",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="#7CFFB2"
        ).pack(pady=(0, 15))

        scroll_frame = ctk.CTkScrollableFrame(
            container,
            fg_color="transparent"
        )

        scroll_frame.pack(
            fill="both",
            expand=True
        )

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

            row = ctk.CTkFrame(
                scroll_frame,
                fg_color="transparent"
            )

            row.pack(
                fill="x",
                pady=8
            )

            ctk.CTkLabel(
                row,
                text=f"Student: {student['name']}",
                width=220,
                anchor="w",
                font=ctk.CTkFont(
                    size=14,
                    weight="bold"
                )
            ).pack(
                side="left",
                padx=(0, 10)
            )

            ctk.CTkButton(
                row,
                text="Select Photo",
                width=130,
                command=lambda i=i: select_photo(i)
            ).pack(
                side="left",
                padx=(0, 10)
            )

            status_label = ctk.CTkLabel(
                row,
                text="No image selected",
                text_color="gray60"
            )

            status_label.pack(side="left")

            self.photo_status_labels.append(status_label)

        error_label.pack(pady=(10, 5))

        def on_start_review():

            if any(
                student["image_path"] is None
                for student in self.students
            ):
                error_label.configure(
                    text="Please select an image for every student before starting."
                )
                return

            self.start_review()

        ctk.CTkButton(
            container,
            text="Start Review",
            width=180,
            height=40,
            fg_color="#1F8F4C",
            hover_color="#27AE60",
            command=on_start_review
        ).pack(pady=(10, 0))

    # -----------------------------------------
    # REVIEW
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

        student = self.students[
            self.current_student_index
        ]

        self.student_label.configure(
            text=f"Student: {student['name']}"
        )

        self.load_and_display(
            student["image_path"]
        )

    def next_student(self):

        self.current_student_index += 1

        if self.current_student_index >= len(self.students):
            self.show_done_screen()
        else:
            self.load_current_student()

    def show_done_screen(self):

        self.clear_main_frame()

        ctk.CTkLabel(
            self.main_frame,
            text="Done",
            font=ctk.CTkFont(
                size=32,
                weight="bold"
            ),
            text_color="#7CFFB2"
        ).pack(expand=True)

    # -----------------------------------------
    # HEADER
    # -----------------------------------------

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

        ctk.CTkLabel(
            self.header,
            text="📷  Image Metadata",
            font=ctk.CTkFont(
                size=28,
                weight="bold"
            ),
            text_color="#7CFFB2"
        ).pack(side="left")

        ctk.CTkLabel(
            self.header,
            text="View image information and EXIF metadata",
            text_color="gray60",
            font=ctk.CTkFont(size=13)
        ).pack(
            side="left",
            padx=15
        )

    # -----------------------------------------
    # CONTENT
    # -----------------------------------------

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

        self.image_viewer = ImageViewer(
            self.content,
            on_drop=self.on_drop
        )

        self.metadata_panel = MetadataPanel(
            self.content
        )

    # -----------------------------------------
    # BOTTOM BAR
    # -----------------------------------------

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

        self.open_button.pack(side="left")

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

        self.exit_button.pack(side="right")

    # -----------------------------------------
    # IMAGE HANDLING
    # -----------------------------------------

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

        if file_path:
            self.load_and_display(file_path)

    def on_drop(self, event):

        file_path = event.data.strip("{}")

        self.load_and_display(file_path)

    def load_and_display(self, file_path):

        try:

            data = load_image(file_path)

            self.current_image = data["image"]
            self.current_data = data

            self.image_viewer.update(
                self.current_image
            )

            self.metadata_panel.update(data)

            add_recent_file(data["path"])
            self.refresh_recent_menu()

        except FileNotFoundError:

            show_error(
                self,
                "File not found."
            )

        except UnidentifiedImageError:

            show_error(
                self,
                "This file is not a valid image."
            )

        except OSError:

            show_error(
                self,
                "Could not open this file."
            )

    # -----------------------------------------
    # RECENT FILES
    # -----------------------------------------

    def refresh_recent_menu(self):

        recent = load_recent_files()

        self.recent_map = {
            Path(path).name: path
            for path in recent
        }

        values = (
            list(self.recent_map.keys())
            or ["No recent files"]
        )

        self.recent_menu.configure(
            values=values
        )

        self.recent_menu.set(values[0])

    def open_recent(self, name):

        file_path = self.recent_map.get(name)

        if file_path:
            self.load_and_display(file_path)

    # -----------------------------------------
    # COPY INFO
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
            f"Make: {exif_value(data['make'])}",
            f"Model: {exif_value(data['model'])}",
            f"Lens Model: {exif_value(data['lens_model'])}",
            f"ISO: {exif_value(data['iso'])}",
            f"Aperture: {exif_value(data['fnum'])}",
            f"Shutter Speed: {exif_value(data['exposure_time'])}",
            f"Focal Length: {exif_value(data['focal'])}",
            f"Date Taken: {exif_value(data['date'])}",
            f"Flash: {exif_value(data['flash'])}",
            f"White Balance: {exif_value(data['white_balance'])}",
        ]

        self.clipboard_clear()
        self.clipboard_append("\n".join(lines))
        self.update()


if __name__ == "__main__":

    app = App()
    app.mainloop()
import customtkinter as ctk
from tkinter import filedialog
from tkinterdnd2 import TkinterDnD
from tkinter import TclError

from pathlib import Path
from PIL import UnidentifiedImageError

from ..core.image import load_image
from ..core.converters import exif_value
from ..core.scoring import grade_student
from ..core.student import ImageRecord
from ..storage.recent_files import load_recent_files, add_recent_file

from .home_screen import HomeScreen
from .image_viewer import ImageViewer
from .metadata_panel import MetadataPanel
from .rule_engine import RuleEngineScreen
from .student_setup import StudentFoldersScreen
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

        # Class / student workflow
        self.class_name = None
        self.student_count = 0
        self.students = []

        # Populated once folders are selected (student_setup.py):
        # one core.student.Student per name, each with its own
        # core.student.ImageRecord list. image_records is the same
        # ImageRecords flattened into the single ordered sequence
        # the review flow steps through.
        self.class_students = []
        self.image_records = []
        self.current_image_index = 0

        # Rule Engine
        self.rule_config = None

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
    # SETUP STEP 1 — HOME PAGE
    # -----------------------------------------

    def show_setup_count_screen(self):
        """
        Home page: Welcome + Previous Classes (placeholder UI) +
        New Class form. Kept under the original method name so
        nothing else in the app has to change how it starts the
        setup flow.
        """

        self.clear_main_frame()

        HomeScreen(
            self.main_frame,
            on_continue=self.on_home_continue
        )

    def on_home_continue(self, class_name, student_count):
        """
        Called by HomeScreen once the New Class form validates.
        Stores class_name for later use and continues the existing
        student-count workflow unchanged.
        """

        self.class_name = class_name
        self.student_count = student_count

        self.show_setup_names_screen()

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
                {"name": name}
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
    # SETUP STEP 3 — SELECT FOLDER PER STUDENT
    # -----------------------------------------

    def show_setup_photos_screen(self):
        """
        Kept under the original method name so nothing else in the
        app has to change how it continues the setup flow. Delegates
        to StudentFoldersScreen (new feature: Select Image -> Select
        Folder, multiple photos per student).
        """

        self.clear_main_frame()

        StudentFoldersScreen(
            self.main_frame,
            students=self.students,
            on_continue=self.on_folders_selected
        )

    def on_folders_selected(self, class_students):
        """
        Called by StudentFoldersScreen once every student has a
        valid, validated photo folder. `class_students` is a list of
        core.student.Student, each already holding one ImageRecord
        per discovered photo. Flatten those into the single ordered
        sequence the review flow steps through, preserving student
        order and each student's own photo order.
        """

        self.class_students = class_students

        self.image_records = [
            image_record
            for student in class_students
            for image_record in student.images
        ]

        self.show_rule_engine_screen()

    # -----------------------------------------
    # RULE ENGINE
    # -----------------------------------------

    def show_rule_engine_screen(self):

        self.clear_main_frame()

        RuleEngineScreen(
            self.main_frame,
            on_continue=self.on_rules_configured
        )

    def on_rules_configured(self, config):
        """
        Applies the professor's System/Human score split to every
        photo in the review queue (new feature: Teacher Grading).
        The split itself always comes from `config` -- nothing here
        hard-codes a specific weighting -- so 40/60, 30/70, etc. all
        just work.
        """

        self.rule_config = config

        for image_record in self.image_records:
            image_record.rule_engine_max_score = config.system_score
            image_record.teacher_max_score = config.human_score

        self.start_review()

    # -----------------------------------------
    # REVIEW
    # -----------------------------------------

    def start_review(self):

        self.current_image_index = 0

        self.clear_main_frame()

        self.create_student_bar()
        self.create_header()
        self.create_content()
        self.create_bottom_bar()

        self.refresh_recent_menu()
        self.load_current_image()

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

    def load_current_image(self):
        """
        Loads and displays the ImageRecord at current_image_index
        (renamed from load_current_student now that the queue is
        photos, not one-per-student).
        """

        image_record = self.image_records[self.current_image_index]

        self.student_label.configure(
            text=f"Student: {image_record.student_name}"
        )

        self.load_and_display(
            str(image_record.image_path),
            image_record=image_record
        )

    def next_image(self):

        self.current_image_index += 1

        if self.current_image_index >= len(self.image_records):
            self.show_done_screen()
        else:
            self.load_current_image()

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
            self.content,
            on_teacher_confirm=self.on_teacher_confirm
        )

    # -----------------------------------------
    # TEACHER GRADING
    # -----------------------------------------

    def on_teacher_confirm(self, image_record):
        """
        Called by TeacherGradingPanel once a Teacher Grading score is
        confirmed for the photo on screen. The ImageRecord already
        carries teacher_score/total_score at this point -- nothing
        else needs to happen yet. Placeholder hook for the next
        stage (Student Average / DataFrame / Final Results), the
        same way HomeScreen.handle_delete_class is a placeholder
        until real storage exists.
        """

        pass

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
            command=self.next_image
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

    def load_and_display(self, file_path, image_record=None):
        """
        Loads `file_path` and renders it. `image_record` is the
        core.student.ImageRecord this photo belongs to during the
        official review flow (student/photo already known, Teacher
        Grading state preserved across re-renders).

        When called without one -- Open Image, drag & drop, or
        Recent Files, all of which can point at any photo outside
        the review queue -- a scratch ImageRecord is created just so
        MetadataPanel / Teacher Grading has something to render. It
        isn't added to self.image_records, so it never affects the
        Next button or the official per-student results.
        """

        try:

            data = load_image(file_path)

            self.current_image = data["image"]
            self.current_data = data

            grading = None

            if self.rule_config is not None:
                grading = grade_student(
                    data,
                    self.rule_config.rules,
                    self.rule_config.system_score
                )

            if image_record is None:
                image_record = ImageRecord(
                    student_name="",
                    image_path=Path(file_path)
                )

            image_record.grading_result = grading

            if grading is not None:
                image_record.rule_engine_score = grading.technical_score
                image_record.rule_engine_max_score = grading.system_score

            if self.rule_config is not None:
                image_record.teacher_max_score = self.rule_config.human_score

            self.image_viewer.update(
                self.current_image
            )

            self.metadata_panel.update(data, image_record)

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

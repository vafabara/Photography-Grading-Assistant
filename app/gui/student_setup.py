import customtkinter as ctk
from tkinter import filedialog
from pathlib import Path

from ..core.image import scan_student_folder, FolderValidationError
from ..core.student import Student, ImageRecord


class StudentFoldersScreen:
    """
    Setup step 3 (replaces the old one-photo-per-student screen --
    new feature: Select Image -> Select Folder). Follows the same
    pattern as RuleEngineScreen/HomeScreen: takes a parent frame and
    an on_continue callback.

    For each student, the professor picks a folder. Every valid
    image inside it is discovered and validated against the folder
    limits (max images / max total size) before the professor can
    continue -- a bad folder shows its error right on that student's
    row instead of crashing or silently dropping images.

    Calls `on_continue(students)` with a list of fully-populated
    core.student.Student objects -- each with its `images` list
    already built as one ImageRecord per discovered photo -- ready
    for the Rule Engine / Teacher Grading review flow.
    """

    def __init__(self, parent, students, on_continue):

        self.on_continue = on_continue

        # One Student per name from the previous (names) screen.
        # folder_path/images get filled in as folders are picked.
        self.class_students = [
            Student(name=entry["name"])
            for entry in students
        ]

        self.container = ctk.CTkFrame(
            parent,
            fg_color="transparent"
        )

        self.container.pack(
            fill="both",
            expand=True,
            padx=40,
            pady=30
        )

        ctk.CTkLabel(
            self.container,
            text="Select a Photo Folder for Each Student",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="#7CFFB2"
        ).pack(pady=(0, 15))

        self.scroll_frame = ctk.CTkScrollableFrame(
            self.container,
            fg_color="transparent"
        )

        self.scroll_frame.pack(
            fill="both",
            expand=True
        )

        self.status_labels = []

        self.error_label = ctk.CTkLabel(
            self.container,
            text="",
            text_color="#FF6B6B"
        )

        self.create_student_rows()

        self.error_label.pack(pady=(10, 5))

        ctk.CTkButton(
            self.container,
            text="Start Review",
            width=180,
            height=40,
            fg_color="#1F8F4C",
            hover_color="#27AE60",
            command=self.handle_continue
        ).pack(pady=(10, 0))

    # -----------------------------------------
    # ROWS
    # -----------------------------------------

    def create_student_rows(self):

        for index, student in enumerate(self.class_students):

            row = ctk.CTkFrame(
                self.scroll_frame,
                fg_color="transparent"
            )

            row.pack(
                fill="x",
                pady=8
            )

            ctk.CTkLabel(
                row,
                text=f"Student: {student.name}",
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
                text="Select Folder",
                width=130,
                command=lambda i=index: self.select_folder(i)
            ).pack(
                side="left",
                padx=(0, 10)
            )

            status_label = ctk.CTkLabel(
                row,
                text="No folder selected",
                text_color="gray60"
            )

            status_label.pack(side="left")

            self.status_labels.append(status_label)

    # -----------------------------------------
    # FOLDER SELECTION
    # -----------------------------------------

    def select_folder(self, index):

        folder_path = filedialog.askdirectory(
            title="Select a photo folder"
        )

        if not folder_path:
            return

        student = self.class_students[index]
        status_label = self.status_labels[index]

        try:
            image_paths = scan_student_folder(folder_path)

        except FolderValidationError as error:

            student.folder_path = None
            student.images = []

            status_label.configure(
                text=f"⚠️ {error}",
                text_color="#FF6B6B"
            )

            return

        student.folder_path = Path(folder_path)

        student.images = [
            ImageRecord(
                student_name=student.name,
                image_path=image_path
            )
            for image_path in image_paths
        ]

        status_label.configure(
            text=f"✅ {len(image_paths)} image(s) found",
            text_color="#7CFFB2"
        )

    # -----------------------------------------
    # VALIDATION / SUBMIT
    # -----------------------------------------

    def handle_continue(self):

        self.error_label.configure(text="")

        if any(not student.images for student in self.class_students):
            self.error_label.configure(
                text="Please select a valid photo folder for every student."
            )
            return

        self.on_continue(self.class_students)

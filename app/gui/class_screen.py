import customtkinter as ctk
from tkinter import filedialog

from ..core.image import scan_student_folder, FolderValidationError
from .widgets import show_error, show_confirm


class ClassScreen:
    """
    The Class Screen (spec sections 8, 9, 11, 12, 14, 15): shows one
    persisted class's students with their photo counts, and lets the
    professor add photos, add a new student, or delete a student.

    Takes a parent frame and a core.class_model.ClassRecord, and
    renders straight from it -- this screen never touches storage
    directly (spec section 17). Folder picking / scanning happens
    here (the same way student_setup.py already does it -- spec
    section 13, no parallel logic), but every resulting change is
    handed back to App through a callback, which persists it via
    storage.class_storage and re-renders this screen with the fresh
    ClassRecord:

        ClassScreen  ->  App  ->  class_storage  ->  classes/<id>/class.json
    """

    def __init__(
        self,
        parent,
        class_record,
        on_back,
        on_open_student,
        on_add_student,
        on_add_photos,
        on_delete_student,
    ):

        self.class_record = class_record
        self.on_back = on_back
        self.on_open_student = on_open_student
        self.on_add_student = on_add_student
        self.on_add_photos = on_add_photos
        self.on_delete_student = on_delete_student

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

        self.create_header()
        self.create_student_list()
        self.create_add_student_button()

    # -----------------------------------------
    # HEADER
    # -----------------------------------------

    def create_header(self):

        header = ctk.CTkFrame(
            self.container,
            fg_color="transparent"
        )

        header.pack(
            fill="x",
            pady=(0, 20)
        )

        ctk.CTkButton(
            header,
            text="← Back",
            width=90,
            height=32,
            fg_color="transparent",
            hover_color="#123f2c",
            border_color="#2ECC71",
            text_color="#7CFFB2",
            border_width=1,
            command=self.on_back
        ).pack(
            side="left",
            padx=(0, 15)
        )

        ctk.CTkLabel(
            header,
            text=self.class_record.class_name,
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="#7CFFB2"
        ).pack(side="left")

    # -----------------------------------------
    # STUDENT LIST
    # -----------------------------------------

    def create_student_list(self):

        card = ctk.CTkFrame(
            self.container,
            corner_radius=12
        )

        card.pack(
            fill="both",
            expand=True,
            pady=(0, 20)
        )

        ctk.CTkLabel(
            card,
            text="Students",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#7CFFB2"
        ).pack(
            anchor="w",
            padx=20,
            pady=(20, 10)
        )

        self.student_list_frame = ctk.CTkScrollableFrame(
            card,
            fg_color="transparent"
        )

        self.student_list_frame.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=(0, 15)
        )

        if not self.class_record.students:

            ctk.CTkLabel(
                self.student_list_frame,
                text="No students yet.",
                text_color="gray60"
            ).pack(pady=20)

            return

        for index, student in enumerate(self.class_record.students):
            self.create_student_row(index, student)

    def create_student_row(self, index, student):

        row = ctk.CTkFrame(
            self.student_list_frame,
            fg_color="transparent"
        )

        row.pack(
            fill="x",
            pady=4
        )

        name_label = ctk.CTkLabel(
            row,
            text=student.name,
            anchor="w",
            width=180,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#7CFFB2",
            cursor="hand2"
        )

        name_label.pack(
            side="left",
            padx=(10, 10)
        )

        name_label.bind(
            "<Button-1>",
            lambda event, i=index: self.on_open_student(self.class_record, i)
        )

        ctk.CTkLabel(
            row,
            text=f"{student.photo_count} photos",
            text_color="gray60"
        ).pack(
            side="left",
            fill="x",
            expand=True
        )

        ctk.CTkButton(
            row,
            text="🗑",
            width=32,
            height=28,
            fg_color="transparent",
            hover_color="#3a1f1f",
            text_color="#FF6B6B",
            command=lambda i=index: self.handle_delete_student(i)
        ).pack(side="right")

        ctk.CTkButton(
            row,
            text="+",
            width=32,
            height=28,
            fg_color="transparent",
            hover_color="#123f2c",
            border_color="#2ECC71",
            border_width=1,
            text_color="#7CFFB2",
            command=lambda i=index: self.handle_add_photos(i)
        ).pack(
            side="right",
            padx=(0, 8)
        )

    # -----------------------------------------
    # ADD PHOTOS (spec section 14)
    # -----------------------------------------

    def handle_add_photos(self, index):

        folder_path = filedialog.askdirectory(
            title="Select a photo folder"
        )

        if not folder_path:
            return

        try:
            image_paths = scan_student_folder(folder_path)
        except FolderValidationError as error:
            show_error(self.container, str(error))
            return

        self.on_add_photos(
            self.class_record,
            index,
            folder_path,
            len(image_paths)
        )

    # -----------------------------------------
    # DELETE STUDENT (spec section 15)
    # -----------------------------------------

    def handle_delete_student(self, index):

        student = self.class_record.students[index]

        show_confirm(
            self.container,
            f'Are you sure you want to remove "{student.name}"?',
            on_yes=lambda: self.on_delete_student(self.class_record, index)
        )

    # -----------------------------------------
    # ADD NEW STUDENT (spec section 12)
    # -----------------------------------------

    def create_add_student_button(self):

        ctk.CTkButton(
            self.container,
            text="+ Add New Student",
            width=200,
            height=40,
            fg_color="#1F8F4C",
            hover_color="#27AE60",
            command=self.open_add_student_dialog
        ).pack(anchor="w")

    def open_add_student_dialog(self):

        dialog = ctk.CTkToplevel(self.container)

        dialog.title("Add New Student")
        dialog.geometry("420x300")
        dialog.resizable(False, False)
        dialog.grab_set()

        ctk.CTkLabel(
            dialog,
            text="Add New Student",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#7CFFB2"
        ).pack(pady=(20, 15))

        ctk.CTkLabel(
            dialog,
            text="Student Name",
            anchor="w",
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(
            anchor="w",
            padx=20
        )

        name_entry = ctk.CTkEntry(
            dialog,
            placeholder_text="Enter student name"
        )

        name_entry.pack(
            fill="x",
            padx=20,
            pady=(5, 15)
        )

        ctk.CTkLabel(
            dialog,
            text="Photo Folder",
            anchor="w",
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(
            anchor="w",
            padx=20
        )

        selected_folder = {"path": None}

        folder_status_label = ctk.CTkLabel(
            dialog,
            text="No folder selected",
            text_color="gray60"
        )

        def select_folder():

            folder_path = filedialog.askdirectory(
                title="Select a photo folder"
            )

            if not folder_path:
                return

            selected_folder["path"] = folder_path

            folder_status_label.configure(
                text=folder_path,
                text_color="#7CFFB2"
            )

        ctk.CTkButton(
            dialog,
            text="Select Folder",
            width=140,
            command=select_folder
        ).pack(
            anchor="w",
            padx=20,
            pady=(5, 5)
        )

        folder_status_label.pack(
            anchor="w",
            padx=20,
            pady=(0, 10)
        )

        error_label = ctk.CTkLabel(
            dialog,
            text="",
            text_color="#FF6B6B"
        )

        error_label.pack(
            anchor="w",
            padx=20
        )

        def handle_add():

            name = name_entry.get().strip()
            folder_path = selected_folder["path"]

            if not name:
                error_label.configure(text="Please enter a student name.")
                return

            if not folder_path:
                error_label.configure(text="Please select a photo folder.")
                return

            try:
                image_paths = scan_student_folder(folder_path)
            except FolderValidationError as error:
                error_label.configure(text=str(error))
                return

            dialog.destroy()

            self.on_add_student(
                self.class_record,
                name,
                folder_path,
                len(image_paths)
            )

        button_row = ctk.CTkFrame(
            dialog,
            fg_color="transparent"
        )

        button_row.pack(pady=(15, 0))

        ctk.CTkButton(
            button_row,
            text="Cancel",
            width=100,
            fg_color="transparent",
            hover_color="#3a1f1f",
            border_color="#FF6B6B",
            border_width=1,
            text_color="#FF6B6B",
            command=dialog.destroy
        ).pack(
            side="left",
            padx=10
        )

        ctk.CTkButton(
            button_row,
            text="Add Student",
            width=140,
            fg_color="#1F8F4C",
            hover_color="#27AE60",
            command=handle_add
        ).pack(
            side="left",
            padx=10
        )

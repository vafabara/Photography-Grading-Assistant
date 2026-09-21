import math
from tkinter import filedialog

import customtkinter as ctk

from ..storage.export import default_export_filename, export_class_to_excel
from .widgets import show_error, show_info


class ClassResultsScreen:
    """
    The Class Results page (new feature): replaces the old "Done"
    screen shown at the end of the review flow. Purely a *view* over
    the already-persisted core.class_model.ClassRecord -- the same
    ClassStudentEntry / ClassPhotoEntry data that already powers the
    Class Screen's Avg Total column and the Student DataFrame. No
    score is computed, recalculated, or duplicated here:

        Photos -> Rule Engine -> Teacher Grading -> ClassRecord
               -> Student DataFrame -> Class Results (this screen)

    Takes a parent frame and a ClassRecord, and calls back into App
    for navigation (Home / Review / a student's details) -- this
    screen never touches class storage itself (same rule as
    ClassScreen / StudentDetailScreen). Export is the one action it
    handles directly: it asks where to save, then hands the
    ClassRecord to storage.export, which builds the workbook.
    """

    def __init__(self, parent, class_record, on_home, on_review, on_student_details):

        self.class_record = class_record
        self.on_home = on_home
        self.on_review = on_review
        self.on_student_details = on_student_details

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
        self.create_completion_message()
        self.create_class_average_card()
        self.create_summary()
        self.create_student_table()
        self.create_bottom_bar()

    # -----------------------------------------
    # HEADER
    # -----------------------------------------

    def create_header(self):

        ctk.CTkLabel(
            self.container,
            text="Class Results",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="#7CFFB2"
        ).pack(pady=(0, 5))

        ctk.CTkLabel(
            self.container,
            text=self.class_record.class_name,
            font=ctk.CTkFont(size=26, weight="bold")
        ).pack(pady=(0, 15))

    # -----------------------------------------
    # COMPLETION MESSAGE
    # -----------------------------------------

    def create_completion_message(self):
        """
        Short status line under the class name. The "grading
        completed" wording is only shown when it's actually true
        (every student Completed) -- this page is also reached after
        grading a single student, when others may still be Pending.
        """

        if not self.class_record.students:
            return

        pending = self.class_record.pending_student_count

        if pending == 0:
            text = (
                "Grading completed successfully. "
                "All student results are ready to review."
            )
            color = "#7CFFB2"
        else:
            noun = "student" if pending == 1 else "students"
            text = f"Grading in progress. {pending} {noun} still pending."
            color = "gray60"

        ctk.CTkLabel(
            self.container,
            text=text,
            text_color=color,
            font=ctk.CTkFont(size=13)
        ).pack(pady=(0, 15))

    # -----------------------------------------
    # CLASS AVERAGE
    # -----------------------------------------

    def create_class_average_card(self):
        """
        Reads ClassRecord.average_total_score -- the mean of every
        graded *photo's* Total Score in the class, not the mean of
        the student averages -- so it's shown exactly as computed.
        """

        average = self.class_record.average_total_score
        graded = self.class_record.graded_photo_count
        total = self.class_record.total_photo_count

        average_text = "—" if math.isnan(average) else f"{average:g} / 100"

        # True when the average is built from only part of the class.
        is_partial = 0 < graded < total

        card = ctk.CTkFrame(
            self.container,
            corner_radius=12
        )

        card.pack(pady=(0, 15))

        ctk.CTkLabel(
            card,
            text="Class Average",
            text_color="gray60",
            font=ctk.CTkFont(size=14)
        ).pack(
            padx=60,
            pady=(12, 0)
        )

        ctk.CTkLabel(
            card,
            text=average_text,
            text_color="#7CFFB2",
            font=ctk.CTkFont(size=28, weight="bold")
        ).pack(
            padx=60,
            pady=(0, 2 if is_partial else 12)
        )

        if is_partial:

            ctk.CTkLabel(
                card,
                text=f"Based on {graded} of {total} photos graded",
                text_color="gray60",
                font=ctk.CTkFont(size=12)
            ).pack(pady=(0, 12))

    # -----------------------------------------
    # CLASS SUMMARY
    # -----------------------------------------

    def create_summary(self):

        summary_text = (
            f"{self.class_record.student_count} Students • "
            f"{self.class_record.total_photo_count} Photos • "
            f"{self.class_record.completed_student_count} Completed • "
            f"{self.class_record.pending_student_count} Pending"
        )

        ctk.CTkLabel(
            self.container,
            text=summary_text,
            text_color="gray60",
            font=ctk.CTkFont(size=14)
        ).pack(pady=(0, 20))

    # -----------------------------------------
    # STUDENT RESULTS TABLE
    # -----------------------------------------

    def create_student_table(self):

        card = ctk.CTkFrame(
            self.container,
            corner_radius=12
        )

        card.pack(
            fill="both",
            expand=True,
            pady=(0, 20)
        )

        if not self.class_record.students:

            ctk.CTkLabel(
                card,
                text="No students in this class.",
                text_color="gray60"
            ).pack(expand=True)

            return

        table_frame = ctk.CTkScrollableFrame(
            card,
            fg_color="transparent"
        )

        table_frame.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=20
        )

        headers = ["Student", "Photos", "Average", "Status"]

        for col_index, header_text in enumerate(headers):

            ctk.CTkLabel(
                table_frame,
                text=header_text,
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color="#7CFFB2"
            ).grid(
                row=0,
                column=col_index,
                padx=15,
                pady=(0, 10),
                sticky="w"
            )

        for row_index, student in enumerate(self.class_record.students, start=1):
            self.create_student_row(table_frame, row_index, student)

    def create_student_row(self, table_frame, row_index, student):
        """
        `student` is a core.class_model.ClassStudentEntry. Average
        and completion status are read straight off it
        (average_total_score / is_completed) -- both already power
        the Class Screen, so nothing here is a second calculation.
        A Pending student always shows "—" for Average, even if a
        partial average could technically be computed.

        The name cell also holds the small "ⓘ" details button, which
        opens that student's per-photo details via
        on_student_details(class_record, student_index). Rows start
        at grid row 1 (row 0 is the header), so the student's index
        in class_record.students is row_index - 1.
        """

        completed = student.is_completed

        if completed:
            avg_score = student.average_total_score
            average_text = "—" if math.isnan(avg_score) else f"{avg_score:g}"
        else:
            average_text = "—"

        name_cell = ctk.CTkFrame(
            table_frame,
            fg_color="transparent"
        )

        name_cell.grid(
            row=row_index,
            column=0,
            padx=15,
            pady=4,
            sticky="w"
        )

        ctk.CTkLabel(
            name_cell,
            text=student.name,
            anchor="w"
        ).pack(side="left")

        ctk.CTkButton(
            name_cell,
            text="ⓘ",
            width=28,
            height=24,
            fg_color="transparent",
            hover_color="#123f2c",
            text_color="#7CFFB2",
            command=lambda i=row_index - 1: self.on_student_details(
                self.class_record, i
            )
        ).pack(
            side="left",
            padx=(8, 0)
        )

        row_values = [str(student.photo_count), average_text]

        for col_index, value in enumerate(row_values, start=1):

            ctk.CTkLabel(
                table_frame,
                text=value,
                anchor="w"
            ).grid(
                row=row_index,
                column=col_index,
                padx=15,
                pady=4,
                sticky="w"
            )

        status_text = "Completed" if completed else "Pending"
        status_color = "#7CFFB2" if completed else "#F5D76E"

        ctk.CTkLabel(
            table_frame,
            text=status_text,
            text_color=status_color,
            font=ctk.CTkFont(weight="bold"),
            anchor="w"
        ).grid(
            row=row_index,
            column=3,
            padx=15,
            pady=4,
            sticky="w"
        )

    # -----------------------------------------
    # BOTTOM ACTIONS — Home / Review / Export
    # -----------------------------------------

    def create_bottom_bar(self):

        bottom_frame = ctk.CTkFrame(
            self.container,
            fg_color="transparent"
        )

        bottom_frame.pack(fill="x")

        ctk.CTkButton(
            bottom_frame,
            text="Home",
            width=140,
            height=40,
            fg_color="transparent",
            hover_color="#123f2c",
            border_color="#2ECC71",
            text_color="#7CFFB2",
            border_width=1,
            command=self.on_home
        ).pack(side="left")

        ctk.CTkButton(
            bottom_frame,
            text="Review",
            width=140,
            height=40,
            fg_color="#1F8F4C",
            hover_color="#27AE60",
            command=self.on_review
        ).pack(
            side="left",
            padx=(10, 0)
        )

        ctk.CTkButton(
            bottom_frame,
            text="Export",
            width=140,
            height=40,
            fg_color="transparent",
            hover_color="#123f2c",
            border_color="#2ECC71",
            text_color="#7CFFB2",
            border_width=1,
            command=self.handle_export
        ).pack(side="right")

    def handle_export(self):
        """
        Ask where to save, then export the class to an .xlsx
        workbook via storage.export.export_class_to_excel. Failures
        are shown as plain messages -- never a traceback.
        """

        file_path = filedialog.asksaveasfilename(
            title="Export Class Results",
            defaultextension=".xlsx",
            filetypes=[("Excel workbook", "*.xlsx")],
            initialfile=default_export_filename(self.class_record.class_name)
        )

        if not file_path:
            return

        # defaultextension isn't applied on every platform.
        if not file_path.lower().endswith(".xlsx"):
            file_path += ".xlsx"

        try:
            export_class_to_excel(self.class_record, file_path)

        except ImportError:
            show_error(
                self.container,
                "Excel export needs the 'openpyxl' package.\n"
                "Install it with: pip install openpyxl"
            )

        except OSError:
            show_error(
                self.container,
                "Could not save the file. Make sure it isn't open in "
                "another program and that you can write to that location."
            )

        except Exception:
            # Last-resort guard at the GUI boundary (e.g. openpyxl
            # rejecting an unusual character in a note): the teacher
            # gets a message instead of a silent failure.
            show_error(
                self.container,
                "Could not export the results."
            )

        else:
            show_info(
                self.container,
                "Export",
                "Results exported successfully."
            )

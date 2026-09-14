import math

import customtkinter as ctk

from .widgets import show_info


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
    for its three bottom actions -- this screen never touches
    storage itself (same rule as ClassScreen / StudentDetailScreen).
    """

    def __init__(self, parent, class_record, on_home, on_review, on_export=None):

        self.class_record = class_record
        self.on_home = on_home
        self.on_review = on_review
        self.on_export = on_export

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
        """

        completed = student.is_completed

        if completed:
            avg_score = student.average_total_score
            average_text = "—" if math.isnan(avg_score) else f"{avg_score:g}"
        else:
            average_text = "—"

        row_values = [student.name, str(student.photo_count), average_text]

        for col_index, value in enumerate(row_values):

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
            column=len(row_values),
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
        Placeholder only (spec: Export is not implemented yet). Uses
        the existing show_info dialog pattern rather than inventing
        a new one, the same way show_error/show_confirm are already
        reused across the app.
        """

        if self.on_export:
            self.on_export()
            return

        show_info(
            self.container,
            "Export",
            "Export is coming soon."
        )

import math
from pathlib import Path

import customtkinter as ctk


def format_score(value):
    """A score for display: "—" if the photo isn't graded, else 84.2 -> "84.2"."""

    if value is None or (isinstance(value, float) and math.isnan(value)):
        return "—"

    return f"{value:g}"


class StudentResultsDetailScreen:
    """
    Per-student details opened from the Class Results screen's "ⓘ"
    button (new feature: Student Details). A read-only view over one
    core.class_model.ClassStudentEntry: the student's average and
    photo count, then one card per photo with its Rule Engine /
    Teacher / Total Score and its saved note.

    Everything shown is read straight from ClassStudentEntry /
    ClassPhotoEntry -- notes come from ClassPhotoEntry.note, the same
    field the Photo Note dialog writes -- so there's no second copy
    of any score or note. Takes a parent frame, a student and an
    on_back callback (App returns to the Class Results screen), the
    same pattern as StudentDetailScreen.

    This is a separate screen from StudentDetailScreen on purpose:
    that one is the Class Screen's DataFrame table (back goes to the
    Class Screen, no notes), and changing it would change a screen
    that already works.
    """

    def __init__(self, parent, student, on_back):

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

        self.create_header(student, on_back)
        self.create_photo_list(student)

    # -----------------------------------------
    # HEADER
    # -----------------------------------------

    def create_header(self, student, on_back):

        header = ctk.CTkFrame(
            self.container,
            fg_color="transparent"
        )

        header.pack(
            fill="x",
            pady=(0, 5)
        )

        ctk.CTkButton(
            header,
            text="← Back to Results",
            width=150,
            height=32,
            fg_color="transparent",
            hover_color="#123f2c",
            border_color="#2ECC71",
            text_color="#7CFFB2",
            border_width=1,
            command=on_back
        ).pack(
            side="left",
            padx=(0, 15)
        )

        ctk.CTkLabel(
            header,
            text=student.name,
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="#7CFFB2"
        ).pack(side="left")

        # Same rule as the Class Results table: a Pending student's
        # average is shown as "—", not a partial number.
        average = student.average_total_score

        if student.is_completed and not math.isnan(average):
            average_text = f"{average:g} / 100"
        else:
            average_text = "—"

        status_text = "Completed" if student.is_completed else "Pending"

        ctk.CTkLabel(
            self.container,
            text=(
                f"Average: {average_text} • "
                f"{student.photo_count} Photos • "
                f"{status_text}"
            ),
            text_color="gray60",
            font=ctk.CTkFont(size=14),
            anchor="w"
        ).pack(
            fill="x",
            pady=(0, 15)
        )

    # -----------------------------------------
    # PHOTO CARDS
    # -----------------------------------------

    def create_photo_list(self, student):

        # Scrollable so a student with many photos (up to the
        # 20-photo folder limit, and more if photos are added later)
        # stays usable.
        photo_list = ctk.CTkScrollableFrame(
            self.container,
            corner_radius=12
        )

        photo_list.pack(
            fill="both",
            expand=True
        )

        if not student.photos:

            ctk.CTkLabel(
                photo_list,
                text="No photos for this student.",
                text_color="gray60"
            ).pack(pady=20)

            return

        for index, photo in enumerate(student.photos, start=1):
            self.create_photo_card(photo_list, index, photo)

    def create_photo_card(self, parent, index, photo):
        """
        `photo` is a core.class_model.ClassPhotoEntry. "Pic N" matches
        the label the Student DataFrame and the Excel export use for
        the same photo, with the filename alongside it.
        """

        card = ctk.CTkFrame(
            parent,
            corner_radius=10
        )

        card.pack(
            fill="x",
            padx=5,
            pady=6
        )

        ctk.CTkLabel(
            card,
            text=f"Pic {index} — {Path(photo.path).name}",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#7CFFB2",
            anchor="w"
        ).pack(
            fill="x",
            padx=15,
            pady=(12, 4)
        )

        scores_row = ctk.CTkFrame(
            card,
            fg_color="transparent"
        )

        scores_row.pack(
            fill="x",
            padx=15
        )

        scores = [
            ("Rule Engine Score", photo.rule_engine_score),
            ("Teacher Score", photo.teacher_score),
            ("Total Score", photo.total_score),
        ]

        for label, value in scores:

            ctk.CTkLabel(
                scores_row,
                text=f"{label}: {format_score(value)}",
                anchor="w"
            ).pack(
                side="left",
                padx=(0, 25)
            )

        note = (photo.note or "").strip()

        ctk.CTkLabel(
            card,
            text="Note",
            text_color="gray60",
            font=ctk.CTkFont(size=12),
            anchor="w"
        ).pack(
            fill="x",
            padx=15,
            pady=(8, 0)
        )

        # wraplength keeps a long note inside the card instead of
        # running off the right edge.
        ctk.CTkLabel(
            card,
            text=note if note else "No note",
            text_color="white" if note else "gray60",
            wraplength=620,
            justify="left",
            anchor="w"
        ).pack(
            fill="x",
            padx=15,
            pady=(0, 12)
        )

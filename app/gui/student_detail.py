import customtkinter as ctk


class StudentDetailScreen:
    """
    The Student Detail Screen (spec section 10).

    Grading (DataFrame, technical/teacher/final scores) doesn't
    exist yet for persisted classes, so this is intentionally just
    an empty state -- no fake data of any kind. This is where that
    per-student grading result will render once that feature is
    built on top of the same ClassRecord/ClassStudentEntry storage
    (spec section 23).
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
        self.create_empty_state()

    def create_header(self, student, on_back):

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

    def create_empty_state(self):

        card = ctk.CTkFrame(
            self.container,
            corner_radius=12
        )

        card.pack(
            fill="both",
            expand=True
        )

        ctk.CTkLabel(
            card,
            text="No grading data available yet.",
            font=ctk.CTkFont(size=16),
            text_color="gray60"
        ).pack(expand=True)

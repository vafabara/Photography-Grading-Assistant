import customtkinter as ctk


class HomeScreen:
    """
    The Home Page (spec: Welcome + Previous Classes + New Class).

    Follows the same pattern as RuleEngineScreen: takes a parent
    frame, builds its own widgets into it, and calls
    `on_continue(class_name, student_count)` once the New Class
    form validates.

    Previous Classes and Delete are UI-only placeholders for now —
    no data source, no persistence, no real delete logic.
    """

    # Placeholder sample data so the Previous Classes card isn't
    # empty. Not connected to any storage — purely cosmetic until a
    # real class database exists.
    SAMPLE_PREVIOUS_CLASSES = [
        "Photography 101 - Fall",
        "Intro to Composition",
    ]

    def __init__(self, parent, on_continue):

        self.on_continue = on_continue

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

        # Two-column layout: left column (Welcome + Previous Classes)
        # and right column (New Class form).
        self.left_column = ctk.CTkFrame(
            self.container,
            fg_color="transparent"
        )

        self.left_column.pack(
            side="left",
            fill="both",
            expand=True,
            padx=(0, 15)
        )

        self.right_column = ctk.CTkFrame(
            self.container,
            fg_color="transparent"
        )

        self.right_column.pack(
            side="left",
            fill="both",
            expand=True,
            padx=(15, 0)
        )

        self.create_welcome_card()
        self.create_previous_classes_card()
        self.create_new_class_card()

    # -----------------------------------------
    # LEFT — WELCOME CARD
    # -----------------------------------------

    def create_welcome_card(self):

        card = ctk.CTkFrame(
            self.left_column,
            corner_radius=12
        )

        card.pack(
            fill="x",
            pady=(0, 15)
        )

        ctk.CTkLabel(
            card,
            text="Welcome to PhotoGrade",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#7CFFB2"
        ).pack(
            anchor="w",
            padx=20,
            pady=(20, 10)
        )

        ctk.CTkLabel(
            card,
            text=(
                "PhotoGrade helps photography instructors evaluate "
                "students' photos using image metadata and technical "
                "grading rules. Create a new class to get started."
            ),
            text_color="gray60",
            font=ctk.CTkFont(size=13),
            justify="left",
            wraplength=380
        ).pack(
            anchor="w",
            padx=20,
            pady=(0, 20)
        )

    # -----------------------------------------
    # LEFT — PREVIOUS CLASSES CARD
    # -----------------------------------------

    def create_previous_classes_card(self):

        card = ctk.CTkFrame(
            self.left_column,
            corner_radius=12
        )

        card.pack(
            fill="both",
            expand=True
        )

        ctk.CTkLabel(
            card,
            text="Previous Classes",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#7CFFB2"
        ).pack(
            anchor="w",
            padx=20,
            pady=(20, 10)
        )

        # Scrollable list so it works the same way once real
        # classes are loaded in later (same pattern used elsewhere
        # in the app for lists, e.g. RuleEngineScreen's factor list).
        self.previous_classes_frame = ctk.CTkScrollableFrame(
            card,
            fg_color="transparent"
        )

        self.previous_classes_frame.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=(0, 15)
        )

        for class_name in self.SAMPLE_PREVIOUS_CLASSES:
            self.create_previous_class_row(class_name)

    def create_previous_class_row(self, class_name):
        """
        One row in the Previous Classes list: class name + a Delete
        icon. Placeholder only — clicking Delete does nothing yet,
        and the row itself isn't clickable/enterable.
        """

        row = ctk.CTkFrame(
            self.previous_classes_frame,
            fg_color="transparent"
        )

        row.pack(
            fill="x",
            pady=4
        )

        ctk.CTkLabel(
            row,
            text=class_name,
            anchor="w",
            font=ctk.CTkFont(size=14)
        ).pack(
            side="left",
            fill="x",
            expand=True,
            padx=(10, 10)
        )

        ctk.CTkButton(
            row,
            text="🗑️",
            width=32,
            height=28,
            fg_color="transparent",
            hover_color="#3a1f1f",
            text_color="#FF6B6B",
            command=lambda: self.handle_delete_class(class_name)
        ).pack(side="right")

    def handle_delete_class(self, class_name):
        """
        Placeholder handler. Intentionally does nothing — no class
        is actually removed and no state changes. Real delete logic
        (and a confirmation step) will be added once classes are
        backed by storage.
        """
        pass

    # -----------------------------------------
    # RIGHT — NEW CLASS CARD
    # -----------------------------------------

    def create_new_class_card(self):

        card = ctk.CTkFrame(
            self.right_column,
            corner_radius=12
        )

        card.pack(
            fill="both",
            expand=True
        )

        ctk.CTkLabel(
            card,
            text="New Class",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#7CFFB2"
        ).pack(
            anchor="w",
            padx=20,
            pady=(20, 15)
        )

        ctk.CTkLabel(
            card,
            text="Class Name",
            anchor="w",
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(
            anchor="w",
            padx=20
        )

        self.class_name_entry = ctk.CTkEntry(
            card,
            placeholder_text="Enter class name"
        )

        self.class_name_entry.pack(
            fill="x",
            padx=20,
            pady=(5, 15)
        )

        ctk.CTkLabel(
            card,
            text="Number of Students",
            anchor="w",
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(
            anchor="w",
            padx=20
        )

        self.student_count_entry = ctk.CTkEntry(
            card,
            placeholder_text="Enter number of students"
        )

        self.student_count_entry.pack(
            fill="x",
            padx=20,
            pady=(5, 15)
        )

        self.error_label = ctk.CTkLabel(
            card,
            text="",
            text_color="#FF6B6B"
        )

        self.error_label.pack(
            anchor="w",
            padx=20,
            pady=(0, 5)
        )

        ctk.CTkButton(
            card,
            text="Next",
            width=150,
            height=40,
            fg_color="#1F8F4C",
            hover_color="#27AE60",
            command=self.handle_next
        ).pack(
            anchor="w",
            padx=20,
            pady=(5, 20)
        )

    # -----------------------------------------
    # VALIDATION / SUBMIT
    # -----------------------------------------

    def handle_next(self):

        self.error_label.configure(text="")

        class_name = self.class_name_entry.get().strip()
        count_value = self.student_count_entry.get().strip()

        if not class_name:
            self.error_label.configure(
                text="Please enter a class name."
            )
            return

        if not count_value.isdigit() or int(count_value) <= 0:
            self.error_label.configure(
                text="Please enter a positive whole number of students."
            )
            return

        self.on_continue(class_name, int(count_value))

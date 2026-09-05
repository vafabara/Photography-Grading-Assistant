import customtkinter as ctk

from ..core.rules import (
    FACTORS,
    RuleError,
    RuleEngineConfig,
    build_rule,
    validate_score_split,
)


class RuleEngineScreen:
    """
    The 'Rule Engine' setup screen (spec section 1-3).

    Lets the professor set a Minimum/Maximum range per metadata
    factor and choose how the total 100 points split between System
    and Human grading. Calls `on_continue(config)` with a
    RuleEngineConfig once the input validates.
    """

    def __init__(self, parent, on_continue):

        self.on_continue = on_continue
        self.factor_entries = {}

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
            text="Rule Engine",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="#7CFFB2"
        ).pack(pady=(0, 5))

        ctk.CTkLabel(
            self.container,
            text=(
                "Set a valid range for each factor. Leave both fields "
                "blank to skip grading that factor."
            ),
            text_color="gray60"
        ).pack(pady=(0, 15))

        self.scroll_frame = ctk.CTkScrollableFrame(
            self.container,
            fg_color="transparent"
        )

        self.scroll_frame.pack(
            fill="both",
            expand=True
        )

        self.create_factor_rows()
        self.create_score_split_row()

        self.error_label = ctk.CTkLabel(
            self.container,
            text="",
            text_color="#FF6B6B"
        )

        self.error_label.pack(pady=(10, 5))

        ctk.CTkButton(
            self.container,
            text="Continue",
            width=150,
            height=40,
            fg_color="#1F8F4C",
            hover_color="#27AE60",
            command=self.handle_continue
        ).pack(pady=(10, 0))

    # -----------------------------------------
    # ROWS
    # -----------------------------------------

    def create_factor_rows(self):

        for factor, info in FACTORS.items():

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
                text=info["label"],
                width=200,
                anchor="w",
                font=ctk.CTkFont(size=14, weight="bold")
            ).pack(
                side="left",
                padx=(0, 10)
            )

            min_entry = ctk.CTkEntry(
                row,
                width=100,
                placeholder_text="Minimum"
            )

            min_entry.pack(
                side="left",
                padx=(0, 10)
            )

            max_entry = ctk.CTkEntry(
                row,
                width=100,
                placeholder_text="Maximum"
            )

            max_entry.pack(side="left")

            self.factor_entries[factor] = (min_entry, max_entry)

    def create_score_split_row(self):

        row = ctk.CTkFrame(
            self.container,
            fg_color="transparent"
        )

        row.pack(
            fill="x",
            pady=(15, 0)
        )

        ctk.CTkLabel(
            row,
            text="System Score (0-100):",
            width=200,
            anchor="w",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(
            side="left",
            padx=(0, 10)
        )

        self.system_score_entry = ctk.CTkEntry(
            row,
            width=100,
            placeholder_text="e.g. 40"
        )

        self.system_score_entry.pack(side="left")

        self.human_score_preview = ctk.CTkLabel(
            row,
            text="Human Score: —",
            text_color="gray60"
        )

        self.human_score_preview.pack(
            side="left",
            padx=(15, 0)
        )

        self.system_score_entry.bind(
            "<KeyRelease>",
            lambda event: self.update_human_score_preview()
        )

    def update_human_score_preview(self):

        value = self.system_score_entry.get().strip()

        if value.isdigit() and 0 <= int(value) <= 100:
            self.human_score_preview.configure(
                text=f"Human Score: {100 - int(value)}"
            )
        else:
            self.human_score_preview.configure(
                text="Human Score: —"
            )

    # -----------------------------------------
    # VALIDATION / SUBMIT
    # -----------------------------------------

    def handle_continue(self):

        self.error_label.configure(text="")

        rules = []

        for factor, (min_entry, max_entry) in self.factor_entries.items():

            min_text = min_entry.get().strip()
            max_text = max_entry.get().strip()

            if not min_text and not max_text:
                continue

            if not min_text or not max_text:
                self.error_label.configure(
                    text=(
                        f"{FACTORS[factor]['label']}: fill in both "
                        f"Minimum and Maximum, or leave both blank."
                    )
                )
                return

            try:
                minimum = float(min_text)
                maximum = float(max_text)
            except ValueError:
                self.error_label.configure(
                    text=f"{FACTORS[factor]['label']}: values must be numbers."
                )
                return

            try:
                rules.append(build_rule(factor, minimum, maximum))
            except RuleError as error:
                self.error_label.configure(text=str(error))
                return

        system_text = self.system_score_entry.get().strip()

        if not system_text.isdigit():
            self.error_label.configure(
                text="System Score must be a whole number between 0 and 100."
            )
            return

        system_score = int(system_text)
        human_score = 100 - system_score

        try:
            validate_score_split(system_score, human_score)
        except RuleError as error:
            self.error_label.configure(text=str(error))
            return

        config = RuleEngineConfig(
            system_score=system_score,
            human_score=human_score,
            rules=rules,
        )

        self.on_continue(config)

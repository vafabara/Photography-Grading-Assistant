import customtkinter as ctk

from ..core.teacher_scoring import (
    validate_teacher_score,
    compute_total_score,
    TeacherScoreError,
)


class TeacherGradingPanel:
    """
    Renders the Rule Engine / Teacher Grading / Total Score
    breakdown for whichever photo is currently on screen (new
    feature: Teacher Grading). Lives inside MetadataPanel's score
    section, the same way HistogramPanel lives inside ImageViewer.

    The System/Human split always comes from whatever is already
    set on the ImageRecord passed to update() (rule_engine_max_score
    / teacher_max_score, which app.py fills in from the existing
    RuleEngineConfig) -- nothing here is hard-coded to a specific
    weighting, so 40/60 and 30/70 both just work. The one exception
    is a photo whose Rule Engine grading came back with
    grading_result.exif_missing True -- app.py has already set that
    photo's teacher_max_score to 100 instead of the configured
    split, and this panel shows "EXIF Missing" in place of a Rule
    Engine score.

    Calls `on_confirm(image_record)` once the professor enters a
    valid score and presses Confirm.
    """

    def __init__(self, parent, on_confirm=None):

        self.on_confirm = on_confirm
        self.image_record = None

        self.frame = ctk.CTkFrame(
            parent,
            fg_color="transparent"
        )

        self.frame.pack(
            fill="x",
            padx=20,
            pady=(0, 10)
        )

        self.rule_engine_label = ctk.CTkLabel(
            self.frame,
            text="Rule Engine: —",
            anchor="w",
            font=ctk.CTkFont(size=14)
        )

        self.rule_engine_label.pack(
            anchor="w",
            pady=(0, 8)
        )

        self.create_teacher_row()

        self.error_label = ctk.CTkLabel(
            self.frame,
            text="",
            text_color="#FF6B6B",
            anchor="w"
        )

        self.error_label.pack(
            anchor="w",
            pady=(4, 8)
        )

        self.total_separator = ctk.CTkFrame(
            self.frame,
            height=1,
            fg_color="gray30"
        )

        self.total_separator.pack(
            fill="x",
            pady=(0, 8)
        )

        self.total_label = ctk.CTkLabel(
            self.frame,
            text="Total Score: —",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color="#7CFFB2",
            anchor="w"
        )

        self.total_label.pack(anchor="w")

    def create_teacher_row(self):

        row = ctk.CTkFrame(
            self.frame,
            fg_color="transparent"
        )

        row.pack(
            fill="x",
            pady=(0, 4)
        )

        ctk.CTkLabel(
            row,
            text="Teacher Grading:",
            anchor="w"
        ).pack(side="left")

        self.teacher_entry = ctk.CTkEntry(
            row,
            width=70,
            placeholder_text="?"
        )

        self.teacher_entry.pack(
            side="left",
            padx=(8, 6)
        )

        self.teacher_max_label = ctk.CTkLabel(
            row,
            text="/ —"
        )

        self.teacher_max_label.pack(side="left")

        self.confirm_button = ctk.CTkButton(
            row,
            text="Confirm",
            width=80,
            fg_color="#1F8F4C",
            hover_color="#27AE60",
            command=self.handle_confirm
        )

        self.confirm_button.pack(
            side="left",
            padx=(12, 0)
        )

    # -----------------------------------------
    # RENDER
    # -----------------------------------------

    def update(self, image_record):
        """
        `image_record` — a core.student.ImageRecord for the photo
        currently on screen. Resets the input box for a fresh photo,
        or re-shows an already-confirmed Teacher score if this exact
        photo was graded before (e.g. the professor navigates back
        to it later, once that becomes possible).
        """

        self.image_record = image_record
        self.error_label.configure(text="")

        grading = image_record.grading_result
        exif_missing = grading is not None and grading.exif_missing

        if exif_missing:
            self.rule_engine_label.configure(
                text="Rule Engine: EXIF Missing"
            )
        elif image_record.rule_engine_score is None:
            self.rule_engine_label.configure(
                text="Rule Engine: — (no rules configured)"
            )
        else:
            self.rule_engine_label.configure(
                text=(
                    f"Rule Engine: {image_record.rule_engine_score:g} "
                    f"/ {image_record.rule_engine_max_score:g}"
                )
            )

        teacher_max = image_record.teacher_max_score

        self.teacher_max_label.configure(
            text=f"/ {teacher_max:g}" if teacher_max is not None else "/ —"
        )

        self.teacher_entry.delete(0, "end")

        if image_record.teacher_score is not None:
            self.teacher_entry.insert(0, f"{image_record.teacher_score:g}")

        self.render_total()

    def render_total(self):

        record = self.image_record

        if record is None or record.total_score is None:
            self.total_label.configure(text="Total Score: ? / 100")
            return

        total_max = (record.rule_engine_max_score or 0) + (record.teacher_max_score or 0)

        self.total_label.configure(
            text=f"Total Score: {record.total_score:g} / {total_max:g}"
        )

    # -----------------------------------------
    # CONFIRM
    # -----------------------------------------

    def handle_confirm(self):

        if self.image_record is None:
            return

        self.error_label.configure(text="")

        record = self.image_record

        if record.teacher_max_score is None:
            self.error_label.configure(
                text="Configure the Rule Engine score split before grading."
            )
            return

        try:
            teacher_score = validate_teacher_score(
                self.teacher_entry.get(),
                record.teacher_max_score
            )
        except TeacherScoreError as error:
            self.error_label.configure(text=str(error))
            return

        record.teacher_score = teacher_score

        rule_engine_score = record.rule_engine_score or 0.0

        record.total_score = compute_total_score(
            rule_engine_score,
            teacher_score
        )

        self.render_total()

        if self.on_confirm:
            self.on_confirm(record)
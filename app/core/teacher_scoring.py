"""
Teacher Grading calculations (new feature: manual professor score
per photo, combined with the Rule Engine score into a Total Score).

This module owns:
  - validating the professor's manual score input for one photo
  - combining Rule Engine + Teacher scores into a Total Score

The System/Human split always comes from the existing
core.rules.RuleEngineConfig (system_score / human_score) that the
professor already set on the Rule Engine screen -- nothing here is
hard-coded to a specific weighting (e.g. 40/60). Whatever split the
professor picked is what image_record.rule_engine_max_score and
image_record.teacher_max_score get set to by app.py.

No CustomTkinter dependency here (spec section 8) -- same rule as
core/rules.py and core/scoring.py. The GUI (gui/teacher_grading.py)
calls into this module and only renders what it returns.
"""


class TeacherScoreError(ValueError):
    """Raised when the professor's manual score input is invalid."""


def validate_teacher_score(raw_value, max_score):
    """
    Validate and parse the professor's manual score input for one
    photo.

    `raw_value` — whatever the professor typed (a string from a
    CTkEntry, in practice).
    `max_score` — this photo's Teacher Grading max score, i.e.
    image_record.teacher_max_score (== rule_config.human_score).

    Returns the parsed float on success.
    Raises TeacherScoreError with a human-readable message if the
    value is missing, not a number, negative, or above `max_score`.
    """

    text = str(raw_value).strip()

    if not text:
        raise TeacherScoreError("Please enter a score.")

    try:
        value = float(text)
    except ValueError:
        raise TeacherScoreError("Score must be a number.")

    if value < 0:
        raise TeacherScoreError("Score cannot be negative.")

    if value > max_score:
        raise TeacherScoreError(f"Score cannot exceed {max_score:g}.")

    return value


def compute_total_score(rule_engine_score, teacher_score):
    """
    Combine an already-graded Rule Engine score with a validated
    Teacher Grading score into the Total Score for one photo.

    Both inputs are expected to already be within their own max
    (the Rule Engine score by construction in core.scoring, the
    Teacher score via validate_teacher_score above) so this is just
    the sum, rounded the same way core.scoring.grade_student rounds
    its final Technical Score.
    """

    return round(rule_engine_score + teacher_score, 1)

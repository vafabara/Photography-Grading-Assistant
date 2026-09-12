"""
Student DataFrame (new feature, spec section 6).

Builds a simple, per-photo pandas DataFrame for one student, read
straight from the already-persisted per-photo scores in
core.class_model.ClassStudentEntry/ClassPhotoEntry -- the same data
that powers the Class Screen's Avg Total column. This module does
not compute or invent any score itself; it only shapes existing
scores into a table.

No CustomTkinter dependency here (spec section 8) -- same rule as
core/rules.py and core/scoring.py. gui/student_detail.py renders
whatever this returns.
"""

import pandas as pd

COLUMNS = ["Photo", "Rule Engine Score", "Teacher Score", "Total Score"]


def build_student_dataframe(student_entry):
    """
    `student_entry` -- a core.class_model.ClassStudentEntry.

    Returns a pandas DataFrame with one row per photo ("Pic 1",
    "Pic 2", ...) followed by a trailing "Average" row. Missing
    scores are NaN (never 0) -- both for individual photos that
    haven't been graded yet, and for the Average of an empty/entirely
    ungraded column.
    """

    rows = [
        {
            "Photo": f"Pic {index}",
            "Rule Engine Score": photo.rule_engine_score,
            "Teacher Score": photo.teacher_score,
            "Total Score": photo.total_score,
        }
        for index, photo in enumerate(student_entry.photos, start=1)
    ]

    dataframe = pd.DataFrame(rows, columns=COLUMNS)

    numeric_columns = ["Rule Engine Score", "Teacher Score", "Total Score"]

    average_row = {"Photo": "Average"}

    for column in numeric_columns:
        average_row[column] = dataframe[column].mean() if not dataframe.empty else float("nan")

    dataframe = pd.concat(
        [dataframe, pd.DataFrame([average_row])],
        ignore_index=True
    )

    return dataframe
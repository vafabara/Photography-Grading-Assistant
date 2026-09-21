import pandas as pd

from app.core.class_model import ClassPhotoEntry, ClassStudentEntry
from app.core.student_dataframe import COLUMNS, build_student_dataframe


def make_student(photos):

    return ClassStudentEntry(
        name="Alice",
        folder_path="/photos/alice",
        photo_count=len(photos),
        photos=photos,
    )


class TestSchema:

    def test_columns_match_the_expected_schema(self):

        df = build_student_dataframe(make_student([]))

        assert list(df.columns) == COLUMNS

    def test_one_row_per_photo_plus_a_trailing_average_row(self):

        photos = [ClassPhotoEntry(path="a.jpg"), ClassPhotoEntry(path="b.jpg")]

        df = build_student_dataframe(make_student(photos))

        assert len(df) == 3  # 2 photos + Average
        assert df.iloc[-1]["Photo"] == "Average"

    def test_photo_labels_are_numbered_in_order(self):

        photos = [ClassPhotoEntry(path="a.jpg"), ClassPhotoEntry(path="b.jpg"), ClassPhotoEntry(path="c.jpg")]

        df = build_student_dataframe(make_student(photos))

        assert list(df["Photo"][:-1]) == ["Pic 1", "Pic 2", "Pic 3"]


class TestValuesArePreserved:

    def test_fully_scored_photo_keeps_its_exact_values(self):

        photos = [
            ClassPhotoEntry(
                path="a.jpg",
                rule_engine_score=35.0,
                teacher_score=50.0,
                total_score=85.0,
            ),
        ]

        df = build_student_dataframe(make_student(photos))
        row = df.iloc[0]

        assert row["Rule Engine Score"] == 35.0
        assert row["Teacher Score"] == 50.0
        assert row["Total Score"] == 85.0

    def test_partially_scored_photo_mixes_real_values_and_nan(self):

        # Rule Engine has run, but the professor hasn't confirmed a
        # Teacher score yet -- so Teacher/Total must stay NaN while
        # Rule Engine Score is a real number.
        photos = [
            ClassPhotoEntry(path="a.jpg", rule_engine_score=28.0),
        ]

        df = build_student_dataframe(make_student(photos))
        row = df.iloc[0]

        assert row["Rule Engine Score"] == 28.0
        assert pd.isna(row["Teacher Score"])
        assert pd.isna(row["Total Score"])

    def test_fully_unscored_photo_is_nan_everywhere_not_zero(self):

        photos = [ClassPhotoEntry(path="a.jpg")]

        df = build_student_dataframe(make_student(photos))
        row = df.iloc[0]

        assert pd.isna(row["Rule Engine Score"])
        assert pd.isna(row["Teacher Score"])
        assert pd.isna(row["Total Score"])
        # Explicitly must not have silently become 0.
        assert row["Total Score"] != 0


class TestAverageRow:

    def test_average_ignores_unscored_photos_rather_than_treating_them_as_zero(self):

        photos = [
            ClassPhotoEntry(path="a.jpg", rule_engine_score=30.0, teacher_score=50.0, total_score=80.0),
            ClassPhotoEntry(path="b.jpg"),  # entirely unscored
        ]

        df = build_student_dataframe(make_student(photos))
        average_row = df.iloc[-1]

        # pandas' mean() skips NaN, so the average must be the single
        # scored photo's value (80.0), not 40.0 (which would mean the
        # unscored photo was silently treated as 0).
        assert average_row["Total Score"] == 80.0

    def test_average_is_nan_when_student_has_no_photos_yet(self):

        df = build_student_dataframe(make_student([]))
        average_row = df.iloc[-1]

        assert average_row["Photo"] == "Average"
        assert pd.isna(average_row["Total Score"])
        assert pd.isna(average_row["Rule Engine Score"])

    def test_average_is_nan_when_no_photo_has_been_graded_yet(self):

        photos = [ClassPhotoEntry(path="a.jpg"), ClassPhotoEntry(path="b.jpg")]

        df = build_student_dataframe(make_student(photos))
        average_row = df.iloc[-1]

        assert pd.isna(average_row["Rule Engine Score"])
        assert pd.isna(average_row["Total Score"])

    def test_average_of_multiple_fully_scored_photos(self):

        photos = [
            ClassPhotoEntry(path="a.jpg", total_score=80.0),
            ClassPhotoEntry(path="b.jpg", total_score=90.0),
        ]

        df = build_student_dataframe(make_student(photos))
        average_row = df.iloc[-1]

        assert average_row["Total Score"] == 85.0


class TestMultipleStudentsInAClass:
    """
    build_student_dataframe only ever builds a table for one
    ClassStudentEntry at a time (that's the real, current API --
    there's no class-wide/multi-student DataFrame function in
    student_dataframe.py, and gui/student_detail.py calls it the
    same way, once per student). So "multiple students" coverage
    means calling the real function once per student inside the
    same class and proving their results stay independent.
    """

    def test_each_students_dataframe_stays_isolated_from_the_others(self):

        alice = ClassStudentEntry(
            name="Alice",
            folder_path="/photos/alice",
            photo_count=2,
            photos=[
                ClassPhotoEntry(path="/photos/alice/1.jpg", rule_engine_score=30.0, teacher_score=50.0, total_score=80.0),
                ClassPhotoEntry(path="/photos/alice/2.jpg"),  # ungraded
            ],
        )

        bob = ClassStudentEntry(
            name="Bob",
            folder_path="/photos/bob",
            photo_count=1,
            photos=[
                ClassPhotoEntry(path="/photos/bob/1.jpg", rule_engine_score=40.0, teacher_score=55.0, total_score=95.0),
            ],
        )

        alice_df = build_student_dataframe(alice)
        bob_df = build_student_dataframe(bob)

        # Every photo appears exactly once, under the student it
        # actually belongs to -- Alice's table never contains Bob's
        # photo (and vice versa), i.e. they're never mixed together.
        assert len(alice_df) == 3   # 2 photos + Average
        assert len(bob_df) == 2     # 1 photo + Average

        alice_photo_rows = alice_df.iloc[:-1]
        bob_photo_rows = bob_df.iloc[:-1]

        assert list(alice_photo_rows["Photo"]) == ["Pic 1", "Pic 2"]
        assert list(bob_photo_rows["Photo"]) == ["Pic 1"]

        # Bob's single (fully scored) photo/value never leaks into
        # Alice's rows, and Alice's values never leak into Bob's.
        assert 95.0 not in list(alice_photo_rows["Total Score"].dropna())
        assert 80.0 not in list(bob_photo_rows["Total Score"].dropna())

        # Each student's Average is computed purely from that
        # student's own available scores, ignoring missing ones
        # rather than treating them as 0.
        alice_average = alice_df.iloc[-1]
        bob_average = bob_df.iloc[-1]

        # Alice: only one of two photos is scored (80.0) -> average
        # is 80.0, not 40.0 (which would mean the ungraded photo was
        # silently counted as a 0).
        assert alice_average["Total Score"] == 80.0
        assert bob_average["Total Score"] == 95.0


import pytest

from app.core.teacher_scoring import (
    TeacherScoreError,
    compute_total_score,
    validate_teacher_score,
)


class TestValidateTeacherScore:

    def test_accepts_a_valid_score_within_range(self):

        assert validate_teacher_score("45", 60) == 45.0

    def test_accepts_the_minimum_score_zero(self):

        assert validate_teacher_score("0", 60) == 0.0

    def test_accepts_the_maximum_allowed_score(self):

        assert validate_teacher_score("60", 60) == 60.0

    def test_accepts_scores_with_decimals(self):

        assert validate_teacher_score("42.5", 60) == 42.5

    def test_rejects_empty_input(self):

        with pytest.raises(TeacherScoreError):
            validate_teacher_score("", 60)

    def test_rejects_whitespace_only_input(self):

        with pytest.raises(TeacherScoreError):
            validate_teacher_score("   ", 60)

    def test_rejects_non_numeric_input(self):

        with pytest.raises(TeacherScoreError):
            validate_teacher_score("abc", 60)

    def test_rejects_negative_scores(self):

        with pytest.raises(TeacherScoreError):
            validate_teacher_score("-5", 60)

    def test_rejects_a_score_just_above_the_max(self):

        with pytest.raises(TeacherScoreError):
            validate_teacher_score("60.1", 60)

    def test_works_with_a_40_60_system_teacher_split(self):

        assert validate_teacher_score("60", 60) == 60.0

    def test_works_with_a_70_30_system_teacher_split(self):

        assert validate_teacher_score("30", 30) == 30.0
        with pytest.raises(TeacherScoreError):
            validate_teacher_score("31", 30)

    def test_works_when_teacher_grading_is_skipped_and_max_is_100(self):

        # Per the Rule Engine's Skip button, teacher_max_score can be
        # set to 100 for all photos.
        assert validate_teacher_score("100", 100) == 100.0


class TestComputeTotalScore:

    def test_sums_rule_engine_and_teacher_scores(self):

        assert compute_total_score(35.0, 50.0) == 85.0

    def test_rounds_to_one_decimal_place(self):

        assert compute_total_score(33.333, 20.111) == round(33.333 + 20.111, 1)

    def test_zero_plus_zero_is_zero(self):

        assert compute_total_score(0.0, 0.0) == 0.0

    def test_max_rule_engine_plus_max_teacher_score(self):

        assert compute_total_score(40.0, 60.0) == 100.0

    def test_result_is_a_plain_number_matching_the_inputs(self):

        # compute_total_score is a straight round(a + b, 1); Python's
        # round() keeps an int result when both inputs are ints, and
        # only produces a float once at least one input is a float
        # (as validate_teacher_score's return value always is).
        assert compute_total_score(10, 20) == 30
        assert isinstance(compute_total_score(10.0, 20.0), float)

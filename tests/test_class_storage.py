import math

import pytest

from app.core.class_model import (
    ClassError,
    ClassPhotoEntry,
    ClassRecord,
    ClassStudentEntry,
    build_class_record,
    new_class_id,
    validate_new_student_name,
)
from app.core.student import ImageRecord, Student
from app.storage import class_storage


@pytest.fixture(autouse=True)
def isolated_classes_dir(tmp_path, monkeypatch):
    """
    Redirect class_storage.CLASSES_DIR to a temporary directory for
    every test in this file, so nothing here ever reads or writes
    the project's real classes/ folder.
    """

    monkeypatch.setattr(class_storage, "CLASSES_DIR", tmp_path)
    return tmp_path


def make_class_record():

    return ClassRecord(
        class_id=new_class_id(),
        class_name="Photography 101",
        students=[
            ClassStudentEntry(
                name="Alice",
                folder_path="/photos/alice",
                photo_count=2,
                photos=[
                    ClassPhotoEntry(
                        path="/photos/alice/1.jpg",
                        rule_engine_score=35.0,
                        teacher_score=50.0,
                        total_score=85.0,
                        note="Great composition",
                    ),
                    ClassPhotoEntry(path="/photos/alice/2.jpg"),
                ],
            ),
            ClassStudentEntry(
                name="Bob",
                folder_path="/photos/bob",
                photo_count=1,
                photos=[
                    ClassPhotoEntry(path="/photos/bob/1.jpg", rule_engine_score=20.0),
                ],
            ),
        ],
    )


# -----------------------------------------
# SAVE / LOAD ROUND TRIP
# -----------------------------------------

class TestSaveAndLoad:

    def test_round_trip_preserves_class_fields(self):

        record = make_class_record()
        class_storage.save_class(record)

        loaded = class_storage.load_class(record.class_id)

        assert loaded.class_id == record.class_id
        assert loaded.class_name == record.class_name
        assert loaded.student_count == 2

    def test_round_trip_preserves_students_and_photo_counts(self):

        record = make_class_record()
        class_storage.save_class(record)

        loaded = class_storage.load_class(record.class_id)

        assert [s.name for s in loaded.students] == ["Alice", "Bob"]
        assert loaded.students[0].photo_count == 2
        assert loaded.students[1].photo_count == 1

    def test_round_trip_preserves_graded_photo_entry_fields(self):

        record = make_class_record()
        class_storage.save_class(record)

        loaded = class_storage.load_class(record.class_id)
        photo = loaded.students[0].photos[0]

        assert photo.path == "/photos/alice/1.jpg"
        assert photo.rule_engine_score == 35.0
        assert photo.teacher_score == 50.0
        assert photo.total_score == 85.0
        assert photo.note == "Great composition"

    def test_round_trip_preserves_ungraded_photo_as_none(self):

        record = make_class_record()
        class_storage.save_class(record)

        loaded = class_storage.load_class(record.class_id)
        ungraded = loaded.students[0].photos[1]

        assert ungraded.rule_engine_score is None
        assert ungraded.teacher_score is None
        assert ungraded.total_score is None
        assert ungraded.note == ""

    def test_load_all_classes_returns_saved_class(self):

        record = make_class_record()
        class_storage.save_class(record)

        all_classes = class_storage.load_all_classes()

        assert len(all_classes) == 1
        assert all_classes[0].class_id == record.class_id

    def test_load_all_classes_empty_when_no_classes_dir_yet(self, tmp_path, monkeypatch):

        # Point CLASSES_DIR at a path that doesn't exist at all
        # (as opposed to an empty existing tmp_path).
        missing_dir = tmp_path / "does_not_exist_yet"
        monkeypatch.setattr(class_storage, "CLASSES_DIR", missing_dir)

        assert class_storage.load_all_classes() == []

    def test_load_class_returns_none_for_unknown_id(self):

        assert class_storage.load_class("does-not-exist") is None

    def test_save_writes_under_isolated_classes_dir_only(self, isolated_classes_dir):

        record = make_class_record()
        class_storage.save_class(record)

        # The class file must exist under the temp dir the fixture
        # pointed CLASSES_DIR at -- never anywhere else.
        expected_file = isolated_classes_dir / record.class_id / "class.json"
        assert expected_file.exists()


class TestDeleteClass:

    def test_delete_removes_the_class(self):

        record = make_class_record()
        class_storage.save_class(record)

        class_storage.delete_class(record.class_id)

        assert class_storage.load_class(record.class_id) is None

    def test_delete_missing_class_does_not_raise(self):

        class_storage.delete_class("never-existed")  # should not raise


class TestLoadAllClassesSkipsCorruptEntries:

    def test_skips_folder_with_invalid_json(self, isolated_classes_dir):

        good_record = make_class_record()
        class_storage.save_class(good_record)

        bad_dir = isolated_classes_dir / "corrupt-id"
        bad_dir.mkdir()
        (bad_dir / "class.json").write_text("{not valid json", encoding="utf-8")

        all_classes = class_storage.load_all_classes()

        assert len(all_classes) == 1
        assert all_classes[0].class_id == good_record.class_id


# -----------------------------------------
# build_class_record / validate_new_student_name
# (core.class_model -- no storage involved)
# -----------------------------------------

class TestBuildClassRecord:

    def test_builds_one_photo_entry_per_discovered_image(self):

        students = [
            Student(
                name="Alice",
                folder_path="/photos/alice",
                images=[
                    ImageRecord(student_name="Alice", image_path="/photos/alice/1.jpg"),
                    ImageRecord(student_name="Alice", image_path="/photos/alice/2.jpg"),
                ],
            ),
        ]

        record = build_class_record("Photo 101", students)

        assert record.class_name == "Photo 101"
        assert record.students[0].photo_count == 2
        assert [p.path for p in record.students[0].photos] == [
            "/photos/alice/1.jpg",
            "/photos/alice/2.jpg",
        ]
        # Freshly built photos must start ungraded.
        assert record.students[0].photos[0].rule_engine_score is None
        assert record.students[0].photos[0].total_score is None

    def test_rejects_duplicate_student_names_case_insensitive(self):

        students = [
            Student(name="Alice", images=[ImageRecord(student_name="Alice", image_path="a.jpg")]),
            Student(name="alice", images=[ImageRecord(student_name="alice", image_path="b.jpg")]),
        ]

        with pytest.raises(ClassError):
            build_class_record("Photo 101", students)

    def test_rejects_blank_class_name(self):

        with pytest.raises(ClassError):
            build_class_record("   ", [])


class TestValidateNewStudentName:

    def test_rejects_blank_name(self):

        record = make_class_record()

        with pytest.raises(ClassError):
            validate_new_student_name(record, "  ")

    def test_rejects_duplicate_name_case_insensitive(self):

        record = make_class_record()

        with pytest.raises(ClassError):
            validate_new_student_name(record, "alice")

    def test_accepts_and_strips_a_new_name(self):

        record = make_class_record()

        assert validate_new_student_name(record, "  Carol  ") == "Carol"


# -----------------------------------------
# ClassStudentEntry / ClassRecord derived properties
# -----------------------------------------

class TestAverageAndCompletionProperties:

    def test_average_total_score_ignores_ungraded_photos(self):

        entry = make_class_record().students[0]  # 85.0 graded + 1 ungraded

        assert entry.average_total_score == 85.0

    def test_average_total_score_is_nan_when_nothing_graded(self):

        entry = ClassStudentEntry(
            name="X", folder_path="", photo_count=1,
            photos=[ClassPhotoEntry(path="x.jpg")],
        )

        assert math.isnan(entry.average_total_score)

    def test_is_completed_false_when_any_photo_ungraded(self):

        entry = make_class_record().students[0]

        assert entry.is_completed is False

    def test_is_completed_true_when_every_photo_scored(self):

        entry = ClassStudentEntry(
            name="X", folder_path="", photo_count=1,
            photos=[ClassPhotoEntry(path="x.jpg", total_score=90.0)],
        )

        assert entry.is_completed is True

    def test_is_completed_false_for_student_with_no_photos(self):

        entry = ClassStudentEntry(name="X", folder_path="", photo_count=0, photos=[])

        assert entry.is_completed is False

    def test_class_record_completed_and_pending_counts(self):

        record = make_class_record()  # Alice pending, Bob pending (no total_score)

        assert record.completed_student_count == 0
        assert record.pending_student_count == 2

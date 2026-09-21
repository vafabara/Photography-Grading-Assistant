"""
Tests for App.find_photo_entry (app/gui/app.py) -- the project's
actual, only mechanism for locating the core.class_model.ClassPhotoEntry
that corresponds to a given core.student.ImageRecord, by matching
image path.

There is no lookup helper for this in core.class_model itself --
find_photo_entry lives on the GUI App class. To keep this a real
unit test rather than a GUI/integration test, App is never
instantiated (App() would build actual CustomTkinter/Tk windows).
Instead the unbound method is called directly against a minimal
stand-in object that only carries the one attribute
(`class_record`) the method actually reads -- this exercises the
exact production code, not a re-implementation of its logic.
"""

import types

from app.core.class_model import ClassPhotoEntry, ClassRecord, ClassStudentEntry
from app.core.student import ImageRecord
from app.gui.app import App


def make_class_record():

    return ClassRecord(
        class_id="class-1",
        class_name="Photography 101",
        students=[
            ClassStudentEntry(
                name="Alice",
                folder_path="/photos/alice",
                photo_count=2,
                photos=[
                    ClassPhotoEntry(path="/photos/alice/1.jpg"),
                    ClassPhotoEntry(path="/photos/alice/2.jpg"),
                ],
            ),
            ClassStudentEntry(
                name="Bob",
                folder_path="/photos/bob",
                photo_count=1,
                photos=[
                    ClassPhotoEntry(path="/photos/bob/1.jpg"),
                ],
            ),
        ],
    )


def call_find_photo_entry(class_record, image_path):
    """
    Call the real App.find_photo_entry as an unbound method, with a
    lightweight stand-in `self` carrying only `class_record` --
    avoids ever constructing App() (which needs a live Tk display).
    """

    dummy_self = types.SimpleNamespace(class_record=class_record)
    image_record = ImageRecord(student_name="", image_path=image_path)

    return App.find_photo_entry(dummy_self, image_record)


def test_find_photo_entry_locates_and_shares_the_real_entry():

    record = make_class_record()

    # A known path returns the correct entry.
    found = call_find_photo_entry(record, "/photos/bob/1.jpg")
    assert found is not None
    assert found.path == "/photos/bob/1.jpg"

    # A non-existing path returns the implementation's actual "not
    # found" result: None.
    assert call_find_photo_entry(record, "/photos/nobody/1.jpg") is None

    # No class currently loaded also returns None, per the method's
    # own documented behavior.
    assert call_find_photo_entry(None, "/photos/bob/1.jpg") is None

    # The returned object is the real ClassPhotoEntry living inside
    # the class model -- not a copy.
    target = call_find_photo_entry(record, "/photos/alice/1.jpg")
    assert target is record.students[0].photos[0]

    # Mutating the returned entry must be visible through the class
    # model directly (read back without going through the lookup
    # again), proving it's the same shared object.
    target.rule_engine_score = 35.0
    target.teacher_score = 50.0
    target.total_score = 85.0
    target.note = "Nice framing"

    stored = record.students[0].photos[0]
    assert stored.rule_engine_score == 35.0
    assert stored.teacher_score == 50.0
    assert stored.total_score == 85.0
    assert stored.note == "Nice framing"

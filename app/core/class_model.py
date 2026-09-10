"""
Data model for a persisted Class (new feature: Class Management).

This is deliberately a *separate* concept from core.student.Student:

  - core.student.Student / ImageRecord hold live, in-memory review
    state (scanned ImageRecord objects, Rule Engine / Teacher scores)
    for whatever review flow is currently on screen.

  - ClassRecord / ClassStudentEntry hold the lightweight, JSON-safe
    summary of a class (name, folder path, photo count) that gets
    written to disk via storage.class_storage so it survives an app
    restart. Nothing here is CustomTkinter-aware or scans folders
    itself -- that stays in core.image / student_setup.py / the
    Class Screen, which pass already-known photo counts in here.

No CustomTkinter dependency here (spec section 8) -- same rule as
core/rules.py and core/scoring.py.
"""

import uuid
from dataclasses import dataclass, field


class ClassError(ValueError):
    """Raised when a Class or Student fails validation."""


@dataclass
class ClassStudentEntry:
    """One student's persisted info within a Class."""

    name: str
    folder_path: str
    photo_count: int


@dataclass
class ClassRecord:
    """
    One persisted Class. `class_id` is a UUID generated once and
    never derived from `class_name` (spec section 19) -- so renaming
    a class later won't need to touch its storage folder.
    """

    class_id: str
    class_name: str
    students: list = field(default_factory=list)  # list[ClassStudentEntry]

    @property
    def student_count(self):
        return len(self.students)

    @property
    def total_photo_count(self):
        return sum(student.photo_count for student in self.students)

    def to_dict(self):
        return {
            "class_id": self.class_id,
            "class_name": self.class_name,
            "student_count": self.student_count,
            "students": [
                {
                    "name": student.name,
                    "folder_path": student.folder_path,
                    "photo_count": student.photo_count,
                }
                for student in self.students
            ],
        }

    @classmethod
    def from_dict(cls, data):

        students = [
            ClassStudentEntry(
                name=entry["name"],
                folder_path=entry["folder_path"],
                photo_count=entry["photo_count"],
            )
            for entry in data.get("students", [])
        ]

        return cls(
            class_id=data["class_id"],
            class_name=data["class_name"],
            students=students,
        )


def new_class_id():
    return str(uuid.uuid4())


def build_class_record(class_name, class_students):
    """
    Build a ClassRecord from a list of core.student.Student objects
    -- the objects StudentFoldersScreen hands back once every
    student has a validated photo folder (spec section 3).

    Raises ClassError if two students share the same name, case
    insensitively (spec section 20).
    """

    class_name = class_name.strip()

    if not class_name:
        raise ClassError("Class name is required.")

    seen_names = set()
    entries = []

    for student in class_students:

        name = student.name.strip()

        if name.lower() in seen_names:
            raise ClassError(f"Duplicate student name: {name}")

        seen_names.add(name.lower())

        entries.append(
            ClassStudentEntry(
                name=name,
                folder_path=str(student.folder_path or ""),
                photo_count=len(student.images),
            )
        )

    return ClassRecord(
        class_id=new_class_id(),
        class_name=class_name,
        students=entries,
    )


def validate_new_student_name(class_record, name):
    """
    Raise ClassError if `name` is blank or already used (case
    insensitively) by another student in `class_record` (spec
    section 20). Returns the stripped name on success.
    """

    name = name.strip()

    if not name:
        raise ClassError("Please enter a student name.")

    existing = {student.name.lower() for student in class_record.students}

    if name.lower() in existing:
        raise ClassError(f'A student named "{name}" already exists in this class.')

    return name

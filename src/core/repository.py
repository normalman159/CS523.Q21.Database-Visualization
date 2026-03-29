from __future__ import annotations
from .models import Student, ValidationError


class StudentRepository:
    """In-memory storage."""

    def __init__(self) -> None:
        self._students: dict[int, Student] = {}

    def all_students(self) -> list[Student]:
        return sorted(self._students.values(), key=lambda s: s.mssv)

    def exists(self, mssv: int) -> bool:
        return mssv in self._students

    def get(self, mssv: int) -> Student | None:
        return self._students.get(mssv)

    def add(self, student: Student) -> None:
        if self.exists(student.mssv):
            raise ValidationError(f"MSSV {student.mssv} đã tồn tại.")
        self._students[student.mssv] = student

    def delete(self, mssv: int) -> Student:
        student = self._students.pop(mssv, None)
        if student is None:
            raise ValidationError(f"Không tìm thấy MSSV {mssv} để xóa.")
        return student

    def clear(self) -> None:
        self._students.clear()

from __future__ import annotations

from dataclasses import dataclass, field

from .btree import BTree
from .models import Student, ValidationError, name_matches_partial, normalize_mssv
from .repository import StudentRepository


@dataclass
class AppState:
    students: list[Student]
    btree_snapshot: dict
    highlighted_node_ids: list[int] = field(default_factory=list)
    selected_mssv: list[int] = field(default_factory=list)
    message: str = ""


class StudentService:
    """Keeps student data and B-tree index in sync."""

    def __init__(self, degree: int = 3) -> None:
        self.repo = StudentRepository()
        self.btree = BTree(t=degree)

    def _state(
        self,
        message: str = "",
        highlighted_node_ids: list[int] | None = None,
        selected_mssv: list[int] | None = None,
    ) -> AppState:
        return AppState(
            students=self.repo.all_students(),
            btree_snapshot=self.btree.export_snapshot(),
            highlighted_node_ids=highlighted_node_ids or [],
            selected_mssv=selected_mssv or [],
            message=message,
        )

    def add_student(self, mssv: int, full_name: str, gender: str) -> AppState:
        student = Student(mssv=mssv, full_name=full_name, gender=gender)
        self.repo.add(student)

        result = self.btree.insert(student.mssv)
        if not result.found:
            self.repo.delete(student.mssv)
            raise ValidationError("MSSV đã tồn tại trong chỉ mục.")

        return self._state(
            message=f"Đã thêm sinh viên {student.mssv}.",
            highlighted_node_ids=result.touched_node_ids,
            selected_mssv=[student.mssv],
        )

    def delete_student(self, mssv: int) -> AppState:
        normalized = normalize_mssv(mssv)
        self.repo.delete(normalized)

        result = self.btree.delete(normalized)
        if not result.found:
            raise ValidationError("Chỉ mục không tìm thấy MSSV cần xóa.")

        return self._state(
            message=f"Đã xóa sinh viên {normalized}.",
            highlighted_node_ids=result.touched_node_ids,
        )

    def search_by_mssv(self, mssv: int) -> AppState:
        normalized = normalize_mssv(mssv)
        path = self.btree.search_path(normalized)
        student = self.repo.get(normalized)

        if student is None:
            return self._state(
                message=f"Không tìm thấy MSSV {normalized}.",
                highlighted_node_ids=path,
            )

        return self._state(
            message=f"Tìm thấy MSSV {normalized}: {student.full_name}.",
            highlighted_node_ids=path,
            selected_mssv=[normalized],
        )

    def search_by_name(self, query: str) -> AppState:
        term = query.strip()
        if not term:
            raise ValidationError("Nhập tên cần tìm.")

        matches = [s.mssv for s in self.repo.all_students() if name_matches_partial(s.full_name, term)]

        if not matches:
            return self._state(message=f"Không tìm thấy tên chứa '{term}'.")

        return self._state(
            message=f"Tìm thấy {len(matches)} sinh viên theo tên '{term}'.",
            selected_mssv=matches,
        )

    def get_initial_state(self) -> AppState:
        return self._state(message="Sẵn sàng.")

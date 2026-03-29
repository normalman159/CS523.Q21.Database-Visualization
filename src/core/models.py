from __future__ import annotations

from dataclasses import dataclass

ALLOWED_GENDERS = {"Nam", "Nu", "Khac"}


class ValidationError(ValueError):
    """Raised when student input fails validation."""


@dataclass(frozen=True)
class Student:
    mssv: int
    full_name: str
    gender: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "mssv", normalize_mssv(self.mssv))
        object.__setattr__(self, "full_name", normalize_name(self.full_name))
        object.__setattr__(self, "gender", normalize_gender(self.gender))


def normalize_mssv(value: object) -> int:
    if not isinstance(value, int) or isinstance(value, bool):
        raise ValidationError("Trường MSSV phải là số nguyên.")
    if value <= 0:
        raise ValidationError("Trường MSSV phải là số nguyên dương.")
    return value


def normalize_name(value: object) -> str:
    if not isinstance(value, str):
        raise ValidationError("Trường họ tên phải là chuỗi.")

    full_name = " ".join(value.strip().split())
    if not full_name:
        raise ValidationError("Trường họ tên không được để trống.")
    return full_name


def normalize_gender(value: object) -> str:
    if not isinstance(value, str):
        raise ValidationError("Trường giới tính phải là chuỗi.")

    gender = value.strip().title()
    mapping = {"Nam": "Nam", "Nu": "Nu", "Nữ": "Nu", "Khac": "Khac", "Khác": "Khac"}
    if gender in mapping:
        gender = mapping[gender]
    if gender not in ALLOWED_GENDERS:
        raise ValidationError("Trường giới tính phải là Nam, Nữ hoặc Khác.")
    return gender


def name_matches_partial(full_name: str, query: str) -> bool:
    return query.strip().lower() in full_name.lower()

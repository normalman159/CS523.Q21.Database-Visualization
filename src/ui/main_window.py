from __future__ import annotations

from typing import cast

from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from core.models import ValidationError
from core.service import AppState, StudentService
from ui.btree_view import BTreeView


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Ứng dụng giả lập hệ quản trị CSDL đơn giản")
        self.resize(1200, 760)

        self.service = StudentService(degree=3)

        self._build_ui()
        self._apply_state(self.service.get_initial_state())

    def _build_ui(self) -> None:
        root = QWidget()
        self.setCentralWidget(root)

        layout = QVBoxLayout(root)

        controls_layout = QGridLayout()
        form_group = QGroupBox("Nhập thông tin sinh viên")
        form_layout = QFormLayout(form_group)
    
        self.mssv_input = QLineEdit()
        self.name_input = QLineEdit()
        self.gender_input = QComboBox()
        self.gender_input.addItems(["Nam", "Nu", "Khac"])

        form_layout.addRow("MSSV", self.mssv_input)
        form_layout.addRow("Họ tên", self.name_input)
        form_layout.addRow("Giới tính", self.gender_input)

        button_box = QGroupBox("Thao tác")
        btn_layout = QVBoxLayout(button_box)

        self.add_btn = QPushButton("Thêm sinh viên")
        self.delete_btn = QPushButton("Xóa theo MSSV")
        self.search_id_btn = QPushButton("Tìm theo MSSV")
        self.search_name_btn = QPushButton("Tìm theo tên")

        for button in [
            self.add_btn,
            self.delete_btn,
            self.search_id_btn,
            self.search_name_btn,
        ]:
            btn_layout.addWidget(button)

        controls_layout.addWidget(form_group, 0, 0)
        controls_layout.addWidget(button_box, 0, 1)

        layout.addLayout(controls_layout)

        middle_layout = QHBoxLayout()

        db_group = QGroupBox("Database (Dữ liệu sinh viên)")
        db_layout = QVBoxLayout(db_group)
        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["MSSV", "Họ tên", "Giới tính"])
        header = cast(QHeaderView, self.table.horizontalHeader())
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        db_layout.addWidget(self.table)

        index_group = QGroupBox("B-tree Index (theo MSSV)")
        index_layout = QVBoxLayout(index_group)
        self.tree_view = BTreeView()
        index_layout.addWidget(self.tree_view)

        middle_layout.addWidget(db_group, 1)
        middle_layout.addWidget(index_group, 1)

        layout.addLayout(middle_layout)

        log_group = QGroupBox("Các thao tác")
        log_layout = QVBoxLayout(log_group)
        self.status_label = QLabel("Sẵn sàng.")
        self.log_view = QTextEdit()
        self.log_view.setReadOnly(True)
        log_layout.addWidget(self.status_label)
        log_layout.addWidget(self.log_view)
        layout.addWidget(log_group)

        self.add_btn.clicked.connect(self._on_add)
        self.delete_btn.clicked.connect(self._on_delete)
        self.search_id_btn.clicked.connect(self._on_search_id)
        self.search_name_btn.clicked.connect(self._on_search_name)

    def _append_log(self, message: str) -> None:
        self.log_view.append(message)

    def _apply_state(self, state: AppState) -> None:
        self._render_table(state)
        self.tree_view.render_tree(state.btree_snapshot, state.highlighted_node_ids)
        self.status_label.setText(state.message)
        if state.message:
            self._append_log(state.message)

    def _render_table(self, state: AppState) -> None:
        self.table.setRowCount(len(state.students))
        selected = set(state.selected_mssv)

        for row, student in enumerate(state.students):
            values = [str(student.mssv), student.full_name, student.gender]
            for col, value in enumerate(values):
                item = QTableWidgetItem(value)
                if student.mssv in selected:
                    item.setBackground(QColor("#86efac"))
                self.table.setItem(row, col, item)

    def _read_mssv_input(self) -> int:
        text = self.mssv_input.text().strip()
        try:
            return int(text)
        except ValueError as exc:
            raise ValidationError("Trường MSSV phải là số nguyên.") from exc

    def _on_add(self) -> None:
        try:
            mssv_val = self._read_mssv_input()
            state = self.service.add_student(
                mssv=mssv_val,
                full_name=self.name_input.text(),
                gender=self.gender_input.currentText(),
            )
            self._apply_state(state)
        except (ValueError, ValidationError) as exc:
            self._show_error(str(exc))

    def _on_delete(self) -> None:
        try:
            mssv_val = self._read_mssv_input()
            state = self.service.delete_student(mssv_val)
            self._apply_state(state)
        except (ValueError, ValidationError) as exc:
            self._show_error(str(exc))

    def _on_search_id(self) -> None:
        try:
            mssv_val = self._read_mssv_input()
            state = self.service.search_by_mssv(mssv_val)
            self._apply_state(state)
        except (ValueError, ValidationError) as exc:
            self._show_error(str(exc))

    def _on_search_name(self) -> None:
        try:
            state = self.service.search_by_name(self.name_input.text())
            self._apply_state(state)
        except ValidationError as exc:
            self._show_error(str(exc))

    def _show_error(self, message: str) -> None:
        QMessageBox.critical(self, "Lỗi", message)
        self._append_log(f"[Lỗi] {message}")

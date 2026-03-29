<p align="center">
<a href="https://www.uit.edu.vn/" title="Trường Đại học Công nghệ Thông tin" style="border: none;">
<img src="https://i.imgur.com/WmMnSRt.png" alt="Trường Đại học Công nghệ Thông tin | University of Information Technology">
</a>
</p>

<h1 align="center"><b>CẤU TRÚC DỮ LIỆU VÀ GIẢI THUẬT NÂNG CAO</b></h1>

<p align="center">
Ứng dụng PyQt6 minh họa quản lý sinh viên và trực quan hóa chỉ mục B-tree theo MSSV.
</p>

## THÔNG TIN
* **Người thực hiện:** Trần Phước Thanh Nhân
* **MSSV:** 24521241    
* **Email**: 24521241@gm.uit.edu.vn

## Giới Thiệu

Đây là một ứng dụng desktop Python dùng PyQt6 để mô phỏng một hệ thống quản lý sinh viên đơn giản đi kèm với trực quan hóa B-tree.

Ứng dụng hiện có các chức năng chính sau:

- Thêm sinh viên theo MSSV, họ tên và giới tính.
- Xóa sinh viên theo MSSV.
- Tìm kiếm theo MSSV.
- Tìm kiếm gần đúng theo họ tên.
- Hiển thị bảng dữ liệu sinh viên và cây B-tree song song.
- Tô sáng các nút B-tree đã đi qua khi tìm kiếm hoặc thao tác chỉ mục.

## Công Nghệ Sử Dụng

- Python 3.13
- PyQt6 cho giao diện đồ họa
- Pytest được khai báo trong môi trường dự án

## Cấu Trúc Dự Án

```text
pyproject.toml
README.md
src/
	main.py
	core/
		btree.py
		models.py
		repository.py
		service.py
	ui/
		btree_view.py
		main_window.py
```

## Yêu Cầu Hệ Thống

- Python 3.13 hoặc mới hơn theo cấu hình hiện tại của dự án
- Windows, macOS, hoặc Linux đều có thể chạy nếu cài được PyQt6

## Cài Đặt

Tạo môi trường ảo nếu chưa có:

```powershell
python -m venv .venv
```

Kích hoạt môi trường ảo trên Windows PowerShell:

```powershell
& .venv\Scripts\Activate.ps1
```

Cài các phụ thuộc của dự án:

```powershell
pip install pyqt6 pytest
```

Nếu bạn đã sử dụng một công cụ quản lý môi trường khác như uv, chỉ cần đảm bảo PyQt6 và Pytest có sẵn trong môi trường đang chạy.

## Chạy Ứng Dụng

Sau khi kích hoạt môi trường ảo, chạy:

```powershell
python src/main.py
```

## Hướng Dẫn Sử Dụng

1. Nhập MSSV, họ tên và giới tính.
2. Bấm **Thêm sinh viên** để lưu bản ghi vào bộ nhớ.
3. Bấm **Tìm theo MSSV** để kiểm tra vị trí của một sinh viên trong chỉ mục B-tree.
4. Bấm **Tìm theo tên** để lọc các sinh viên có họ tên chứa chuỗi nhập vào.
5. Bấm **Xóa theo MSSV** để xóa bản ghi tương ứng.

Kết quả sẽ được phản ánh đồng thời ở:

- Bảng danh sách sinh viên ở bên trái.
- Biểu đồ B-tree ở bên phải.
- Khung trạng thái và nhật ký thao tác ở phía dưới.

## Ràng Buộc Dữ Liệu

- MSSV phải là số nguyên dương.
- Họ tên không được để trống.
- Giới tính hợp lệ: `Nam`, `Nu`, `Khac`.
- Giá trị nhập như `Nữ` và `Khác` được chuẩn hóa về dạng nội bộ tương ứng.
import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import mysql.connector

from qlsanpham import FrmSanPham
from nhacungcap import FrmNhaCungCap
from qlhoadonban import FrmHoaDonBan
from qlhoadonmua import FrmHoaDonMua
from qlkhachhang import QLKhachHang
from thongke import FrmThongKe


# ====== Kết nối MySQL ======
# def connect_db():
#     return mysql.connector.connect(
#         host="localhost",
#         user="root", # thay bằng user MySQL của bạn
#         password="123456", # thay bằng password MySQL của bạn
#         database="qltnd"
# )

# ====== Hàm canh giữa cửa sổ ======
def center_window(win, w=800, h=700):
    ws = win.winfo_screenwidth()
    hs = win.winfo_screenheight()
    x = (ws // 2) - (w // 2)
    y = (hs // 2) - (h // 2)
    win.geometry(f'{w}x{h}+{x}+{y}')

def show_menu():
    main = tk.Tk()
    main.title("HỆ THỐNG QUẢN LÝ CỬA HÀNG MUA BÁN THUỐC NÔNG DƯỢC")
    center_window(main, 720, 420)

    # Thanh menu
    menubar = tk.Menu(main)
    
    # Quản lý
    m_quanly = tk.Menu(menubar, tearoff=0)
    m_quanly.add_command(label="Quản lý sản phẩm", command=lambda: FrmSanPham(main))
    m_quanly.add_command(label="Quản lý mua hàng", command=lambda: FrmHoaDonMua(main))
    m_quanly.add_command(label="Quản lý bán hàng", command=lambda: FrmHoaDonBan(main))


    menubar.add_cascade(label="Quản lý", menu=m_quanly)
    # QL Nhà cung cấp & Khách hàng
    m_ncc_kh = tk.Menu(menubar, tearoff=0)
    m_ncc_kh.add_command(label="Quản lý nhà cung cấp", command=lambda: FrmNhaCungCap(main))
    m_ncc_kh.add_command(label="Quản lý khách hàng", command=lambda: QLKhachHang(main))

    menubar.add_cascade(label="Nhà cung cấp & Khách hàng", menu=m_ncc_kh)

    menubar.add_cascade(label="Thống kê", command=lambda: FrmThongKe(main))
    menubar.add_command(label="Thoát", command=main.destroy)
    # ====== Chạy ứng dụng ======
    main.config(menu=menubar)
    main.mainloop()

if __name__ == "__main__":
    show_menu()
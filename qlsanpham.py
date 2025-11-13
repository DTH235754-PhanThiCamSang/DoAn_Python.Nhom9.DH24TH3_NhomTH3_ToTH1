import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import mysql.connector
from mysql.connector import IntegrityError
import re
# from connectdb import connect_db

# ====== Kết nối MySQL ======
def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",  
        password="123456",  
        database="qltnd"
    )

# ktra masp
MASP_PATTERN = re.compile(r'^[A-Z]{3}\d{3}$')
def normalize_masp(s: str) -> str:
    return s.strip().upper()

def kiem_tra_masp(masp: str) -> bool:
    masp = masp.strip().upper()
    if not MASP_PATTERN.match(masp):
        messagebox.showwarning(
            "Sai định dạng Mã SP",
            "Mã sản phẩm phải có 3 chữ và 3 số (VD: ABC123)"
        )
        return False
    return True

# ====== Hàm canh giữa cửa sổ ======
def center_window(win, w=900, h=700):
    ws = win.winfo_screenwidth()
    hs = win.winfo_screenheight()
    x = (ws // 2) - (w // 2)
    y = (hs // 2) - (h // 2)
    win.geometry(f'{w}x{h}+{x}+{y}')


class FrmSanPham(tk.Toplevel):
    def __init__(self, parent, connect_db_func=connect_db):
        super().__init__(parent)
        self.connect_db = connect_db_func
        self.title("QUẢN LÝ CỬA HÀNG MUA BÁN THUỐC NÔNG DƯỢC")
        center_window(self, 900, 700)
        self.resizable(False, False)

        # ====== Tiêu đề ======
        self.lbl_title = tk.Label(self, text="QUẢN LÝ SẢN PHẨM", font=("Arial", 16, "bold"))
        self.lbl_title.pack(pady=10)

        # ====== Frame nhập thông tin ======
        frame_info = tk.Frame(self)
        frame_info.pack(pady=5, padx=10, fill="x")

        tk.Label(frame_info, text="Mã sản phẩm").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.entry_ma_sp = tk.Entry(frame_info, width=12)
        self.entry_ma_sp.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        tk.Label(frame_info, text="Tên sản phẩm").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.entry_ten_sp = tk.Entry(frame_info, width=25)
        self.entry_ten_sp.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        tk.Label(frame_info, text="Loại sản phẩm").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.cbb_loai_sp = ttk.Combobox(
            frame_info,
            values=[
                "Thuốc trừ sâu - rầy",
                "Thuốc trừ bệnh",
                "Thuốc trừ cỏ",
                "Phân bón",
                "Thuốc điều hòa sinh trưởng"
            ],
            width=25
        )
        self.cbb_loai_sp.grid(row=0, column=3, padx=5, pady=5, sticky="w")

        tk.Label(frame_info, text="Đơn vị tính").grid(row=1, column=2, padx=5, pady=5, sticky="w")
        self.cbb_don_vi_tinh = ttk.Combobox(
            frame_info,
            values=["Bao", "Gói", "Chai", "Thùng"],
            width=20
        )
        self.cbb_don_vi_tinh.grid(row=1, column=3, padx=5, pady=5, sticky="w")

        tk.Label(frame_info, text="Giá bán").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.entry_gia_ban = tk.Entry(frame_info, width=15)
        self.entry_gia_ban.grid(row=2, column=1, padx=5, pady=5, sticky="w")

        tk.Label(frame_info, text="Hạn sử dụng").grid(row=2, column=2, padx=5, pady=5, sticky="w")
        self.date_entry = DateEntry(
            frame_info,
            width=12,
            background="darkblue",
            foreground="white",
            date_pattern="yyyy-mm-dd"
        )
        self.date_entry.grid(row=2, column=3, padx=5, pady=5, sticky="w")

        # ==== Mma nhà cung cấp COMBOBOX ====
        tk.Label(frame_info, text="Mã Nhà Cung Cấp").grid(row=3, column=2, padx=5, pady=5, sticky="w")
        self.cbb_ma_ncc = ttk.Combobox(frame_info, width=20, state="readonly")
        self.cbb_ma_ncc.grid(row=3, column=3, padx=5, pady=5, sticky="w")
        self.load_mancc_to_combo()  # load mã NCC từ bảng nhacungcap

        # tim kiem
        self.entry_tim_kiem = tk.Entry(frame_info, width=25)
        self.entry_tim_kiem.grid(row=2, column=4, padx=5, pady=5, sticky="w")

        # ====== Bảng danh sách san pham ======
        lbl_ds = tk.Label(self, text="Danh sách sản phẩm", font=("Arial", 11, "bold"))
        lbl_ds.pack(pady=5, anchor="w", padx=10)
        columns = ("masp", "tensp", "loaisp", "dvt", "giaban", "hsd", "mancc")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=10)
        for col in columns:
            self.tree.heading(col, text=col.capitalize())

        self.tree.column("masp", width=50, anchor="center")
        self.tree.column("tensp", width=150)
        self.tree.column("loaisp", width=150)
        self.tree.column("dvt", width=60)
        self.tree.column("giaban", width=50)
        self.tree.column("hsd", width=150)
        self.tree.column("mancc", width=80, anchor="center")
        self.tree.pack(padx=10, pady=5, fill="both")

        # ====== HÀM PHỤ ======
        def xoatext():
            self.entry_ma_sp.config(state='normal')
            self.entry_ma_sp.delete(0, tk.END)
            self.entry_ten_sp.delete(0, tk.END)
            self.entry_gia_ban.delete(0, tk.END)
            self.entry_tim_kiem.delete(0, tk.END)
            self.cbb_loai_sp.set("")
            self.cbb_don_vi_tinh.set("")
            self.cbb_ma_ncc.set("")

        def load_data():
            for i in self.tree.get_children():
                self.tree.delete(i)
            conn = connect_db()
            cur = conn.cursor()
            cur.execute("SELECT * FROM sanpham")
            for row in cur.fetchall():
                self.tree.insert("", tk.END, values=list(row))
            conn.close()
            xoatext()

        def them_sp(self):
            masp = self.entry_ma_sp.get().strip().upper()
            if not kiem_tra_masp(masp):
                return

            tensp = self.entry_ten_sp.get()
            loaisp = self.cbb_loai_sp.get()
            dvt = self.cbb_don_vi_tinh.get()
            giaban1 = self.entry_gia_ban.get()
            hsd = self.date_entry.get()
            mancc = self.cbb_ma_ncc.get().strip()

            if masp == "" or tensp == "" or loaisp == "" or dvt == "" or giaban1 == "" or hsd == "" or mancc == "":
                messagebox.showwarning("Thiếu dữ liệu.", "Vui lòng nhập đủ thông tin")
                return

            giaban = float(giaban1)
            if giaban <= 0:
                messagebox.showwarning("Dữ liệu không hợp lệ", "Giá bán phải là số > 0")
                return

            conn = connect_db()
            cur = conn.cursor()
            try:
                cur.execute(
                    "INSERT INTO sanpham VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (masp, tensp, loaisp, dvt, giaban, hsd, mancc)
                )
                conn.commit()
                load_data()
            except Exception as e:
                messagebox.showerror("Lỗi", str(e))
            finally:
                conn.close()

        def xoa_sp():
            selected = self.tree.selection()
            if not selected:
                messagebox.showwarning("Chưa chọn", "Hãy chọn sản phẩm để xóa")
                return
            masp = self.tree.item(selected)["values"][0]
            conn = connect_db()
            cur = conn.cursor()
            cur.execute("DELETE FROM sanpham WHERE masp=?", (masp,))
            conn.commit()
            conn.close()
            load_data()

        def sua_sp(self):
            selected = self.tree.selection()
            if not selected:
                messagebox.showwarning("Chưa chọn", "Hãy chọn sản phẩm để sửa")
                return
            values = self.tree.item(selected)["values"]
            self.entry_ma_sp.config(state='normal')
            self.entry_ma_sp.delete(0, tk.END)
            self.entry_ma_sp.insert(0, values[0])
            self.entry_ma_sp.config(state='disabled')
            self.entry_ten_sp.delete(0, tk.END)
            self.entry_ten_sp.insert(0, values[1])
            self.cbb_loai_sp.set(values[2])
            self.cbb_don_vi_tinh.set(values[3])
            self.entry_gia_ban.delete(0, tk.END)
            self.entry_gia_ban.insert(0, values[4])
            self.date_entry.set_date(values[5])
            self.cbb_ma_ncc.set(values[6])

        def luu_sp(self):
            masp = self.entry_ma_sp.get().strip().upper()
            if not kiem_tra_masp(masp):
                return

            tensp = self.entry_ten_sp.get()
            loaisp = self.cbb_loai_sp.get()
            dvt = self.cbb_don_vi_tinh.get()
            giaban1 = self.entry_gia_ban.get()
            hsd = self.date_entry.get()
            mancc = self.cbb_ma_ncc.get().strip()

            

            if not mancc:
                messagebox.showwarning("Thiếu dữ liệu", "Chưa chọn Mã Nhà Cung Cấp")
                return

            giaban = float(giaban1)
            if giaban <= 0:
                messagebox.showwarning("Dữ liệu không hợp lệ", "Giá bán phải là số > 0")
                self.entry_gia_ban.focus_set()
                return

            conn = connect_db()
            cur = conn.cursor()
            cur.execute(
                """UPDATE sanpham
                   SET tensp=?, loaisp=?, dvt=?, giaban=?, hsd=?, mancc=?
                   WHERE masp=?""",
                (tensp, loaisp, dvt, giaban, hsd, mancc, masp)
            )
            conn.commit()
            conn.close()
            load_data()

        # ----- Tìm kiếm -----
        def tim_kiem(self):
            tu_khoa = self.entry_tim_kiem.get()
            for i in self.tree.get_children():
                self.tree.delete(i)

            sql = """SELECT masp, tensp, loaisp, dvt, giaban, hsd, mancc FROM sanpham"""
            params = ()

            if tu_khoa:
                sql += " WHERE tensp LIKE ? ORDER BY masp DESC"
                like = f"%{tu_khoa}%"
                params = (like,)
            else:
                sql += " ORDER BY masp DESC"

            conn = connect_db()
            cur = conn.cursor()
            cur.execute(sql, params)

            for row in cur.fetchall():
                row = list(row)
                row[5] = row[5].strftime("%Y-%m-%d") if row[5] else ""
                self.tree.insert("", tk.END, values=row)

            cur.close()
            conn.close()

        # ====== Frame nút ======
        frame_btn = tk.Frame(self)
        frame_btn.pack(pady=5)
        tk.Button(frame_btn, text="Thêm", width=8, command=self.them_sp).grid(row=0, column=0, padx=5)
        tk.Button(frame_btn, text="Lưu", width=8, command=self.luu_sp).grid(row=0, column=1, padx=5)
        tk.Button(frame_btn, text="Sửa", width=8, command=self.sua_sp).grid(row=0, column=2, padx=5)
        tk.Button(frame_btn, text="Hủy", width=8, command=self.xoatext).grid(row=0, column=3, padx=5)
        tk.Button(frame_btn, text="Xóa", width=8, command=self.xoa_sp).grid(row=0, column=4, padx=5)
        tk.Button(frame_btn, text="Đóng", width=8, command=self.destroy).grid(row=0, column=5, padx=5)

        tk.Button(frame_info, text="Tìm kiếm", width=8, command=self.tim_kiem).grid(row=2, column=5, padx=5, pady=5, sticky="w")
        tk.Button(frame_info, text="Tải lại", width=8, command=self.load_data).grid(row=3, column=5, padx=5, pady=5, sticky="w")

        load_data()

    # ====== load mancc vào combobox ======
    def load_mancc_to_combo(self):
        try:
            conn = connect_db()
            cur = conn.cursor()
            cur.execute("SELECT mancc FROM nhacungcap ORDER BY mancc")
            rows = cur.fetchall()
            conn.close()
            ds = [r[0] for r in rows]
            self.cbb_ma_ncc["values"] = ds
            if ds:
                self.cbb_ma_ncc.current(0)
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không tải được danh sách nhà cung cấp\n{e}")


if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    FrmSanPham(root)
    root.mainloop()

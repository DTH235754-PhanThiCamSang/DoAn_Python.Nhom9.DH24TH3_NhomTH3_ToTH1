import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from tkcalendar import DateEntry
from datetime import date
import re
from mysql.connector import IntegrityError  
# from connectdb import connect_db

# ====== Kết nối DB ======
def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="123456",
        database="qltnd"
    )


def center_window(win, w=900, h=700):
    ws = win.winfo_screenwidth()
    hs = win.winfo_screenheight()
    x = (ws // 2) - (w // 2)
    y = (hs // 2) - (h // 2)
    win.geometry(f"{w}x{h}+{x}+{y}")

def kiem_tra_makh(makh: str) -> bool:
   
    if not makh:
        messagebox.showwarning("Thiếu dữ liệu", "Phải nhập mã khách hàng")
        return False
    if not re.fullmatch(r"[A-Z]{3}\d{3}", makh):
        messagebox.showwarning("Sai định dạng", "Mã khách hàng phải dạng KH001 (3 chữ + 3 số)")
        return False
    return True


class QLKhachHang(tk.Toplevel):
    def __init__(self, parent, connect_db_func=connect_db, kiem_tra_makh_func=kiem_tra_makh):
        super().__init__(parent)

       
        self.connect_db    = connect_db_func
        self.kiem_tra_makh = kiem_tra_makh_func

        # cấu hình cửa sổ con
        self.title("QUẢN LÝ CỬA HÀNG MUA BÁN THUỐC NÔNG DƯỢC")
        center_window(self, 900, 700)
        self.resizable(False, False)

        # ====== TIÊU ĐỀ ======
        lbl_title = tk.Label(
            self,
            text="QUẢN LÝ KHÁCH HÀNG ",
            font=("Arial", 16, "bold")
        )
        lbl_title.pack(pady=10)

        # ====== Frame nhập thông tin ======
        frame_info = tk.Frame(self)
        frame_info.pack(pady=5, padx=10, fill="x")

        tk.Label(frame_info, text="Mã khách hàng").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.entry_ma_kh = tk.Entry(frame_info, width=12)
        self.entry_ma_kh.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        tk.Label(frame_info, text="Tên khách hàng").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.entry_ten_kh = tk.Entry(frame_info, width=25)
        self.entry_ten_kh.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        tk.Label(frame_info, text="Loại khách hàng").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.cbb_loaikh = ttk.Combobox(
            frame_info,
            values=["Nông dân","Hợp tác xã"],
            width=25,
            state="readonly"
        )
        self.cbb_loaikh.grid(row=0, column=3, padx=5, pady=5, sticky="w")

        tk.Label(frame_info, text="Địa chỉ").grid(row=1, column=2, padx=5, pady=5, sticky="w")
        self.entry_dia_chi = tk.Entry(frame_info, width=25)
        self.entry_dia_chi.grid(row=1, column=3, padx=5, pady=5, sticky="w")

        tk.Label(frame_info, text="Số điện thoại").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.entry_sdt = tk.Entry(frame_info, width=15)
        self.entry_sdt.grid(row=2, column=1, padx=5, pady=5, sticky="w")

        # Tìm kiếm
        tk.Label(frame_info, text="Từ khóa").grid(row=2, column=2, padx=5, pady=5, sticky="w")
        self.entry_tim_kiem = tk.Entry(frame_info, width=25)
        self.entry_tim_kiem.grid(row=2, column=3, padx=5, pady=5, sticky="w")
        tk.Button(frame_info, text="Tìm kiếm", width=8, command=self.tim_kiem).grid(row=2, column=4, padx=5)
        tk.Button(frame_info, text="Tải lại", width=8, command=self.load_data).grid(row=2, column=5, padx=5)

        # ====== Bảng ======
        tk.Label(self, text="Danh sách khách hàng", font=("Arial", 10, "bold")).pack(pady=5, anchor="w", padx=10)
        columns = ("makh", "tenkh", "loaikh", "diachi", "sdt")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=10)
        for c in columns:
            self.tree.heading(c, text=c.upper())
        self.tree.column("makh", width=80, anchor="center")
        self.tree.column("tenkh", width=180)
        self.tree.column("loaikh", width=140)
        self.tree.column("diachi", width=220)
        self.tree.column("sdt", width=120, anchor="center")
        self.tree.pack(padx=10, pady=5, fill="both", expand=True)

        # ====== Nút ======
        frame_btn = tk.Frame(self)
        frame_btn.pack(pady=5)
        tk.Button(frame_btn, text="Thêm", width=8, command=self.them_kh).grid(row=0, column=0, padx=5)
        tk.Button(frame_btn, text="Lưu", width=8, command=self.luu_kh).grid(row=0, column=1, padx=5)
        tk.Button(frame_btn, text="Sửa", width=8, command=self.sua_kh).grid(row=0, column=2, padx=5)
        tk.Button(frame_btn, text="Hủy", width=8, command=self.xoatext).grid(row=0, column=3, padx=5)
        tk.Button(frame_btn, text="Xóa", width=8, command=self.xoa_kh).grid(row=0, column=4, padx=5)
        tk.Button(frame_btn, text="Thoát", width=8, command=self.destroy).grid(row=0, column=5, padx=5)
       
        # Khởi tạo
        self.xoatext()
        self.load_data()

        
    # ====== CRUD & Search ======
    def xoatext(self):
        self.entry_ma_kh.config(state="normal"); self.entry_ma_kh.delete(0, tk.END)
        self.entry_ten_kh.delete(0, tk.END)
        self.cbb_loaikh.set("")
        self.entry_dia_chi.delete(0, tk.END)
        self.entry_sdt.delete(0, tk.END)
        self.entry_tim_kiem.delete(0, tk.END)

    def load_data(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        conn = self.connect_db()
        cur = conn.cursor()
        cur.execute("SELECT makh, tenkh, loaikh, diachi, sdt FROM khachhang ORDER BY makh DESC")
        for row in cur.fetchall():
            self.tree.insert("", tk.END, values=list(row))
        cur.close(); conn.close()

    def them_kh(self):
        makh   = self.entry_ma_kh.get().strip().upper()
        if not self.kiem_tra_makh(makh):
            return
        tenkh  = self.entry_ten_kh.get().strip()
        loaikh = self.cbb_loaikh.get().strip()
        diachi = self.entry_dia_chi.get().strip()
        sdt    = self.entry_sdt.get().strip()


        if not all([makh, tenkh, loaikh, sdt]):
            messagebox.showwarning("Thiếu dữ liệu", "Mã/Tên/Loại KH và SĐT là bắt buộc")
            return

        if not re.fullmatch(r"0\d{9}", sdt):
            messagebox.showwarning("Dữ liệu không hợp lệ", "Số điện thoại phải gồm 10 chữ số và bắt đầu bằng 0!")
            self.entry_sdt.focus_set()
            return

        conn = self.connect_db(); cur = conn.cursor()
        try:
            cur.execute(
                "INSERT INTO khachhang (makh, tenkh, loaikh, diachi, sdt) VALUES (?,?,?,?,?)",
                (makh, tenkh, loaikh, diachi, sdt)
            )
            conn.commit()
            self.load_data()
            self.xoatext()
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))
        finally:
            cur.close(); conn.close()

    def sua_kh(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Chưa chọn", "Hãy chọn khách hàng để sửa")
            return
        v = self.tree.item(sel)["values"]
        self.xoatext()
        self.entry_ma_kh.insert(0, v[0])
        self.entry_ma_kh.config(state="disabled")
        self.entry_ten_kh.insert(0, v[1])
        self.cbb_loaikh.set(v[2])
        self.entry_dia_chi.insert(0, v[3])
        self.entry_sdt.insert(0, str(v[4]))

    def luu_kh(self):
        makh   = self.entry_ma_kh.get().strip().upper()
        if not self.kiem_tra_makh(makh):
            return
        tenkh  = self.entry_ten_kh.get().strip()
        loaikh = self.cbb_loaikh.get().strip()
        diachi = self.entry_dia_chi.get().strip()
        sdt    = self.entry_sdt.get().strip()
        if len(sdt) == 9 and sdt.isdigit():
            sdt = "0" + sdt

        if not re.fullmatch(r"0\d{9}", sdt):
            messagebox.showwarning("Dữ liệu không hợp lệ", "Số điện thoại phải gồm 10 chữ số và bắt đầu bằng 0!")
            self.entry_sdt.focus_set()
            return

        conn = self.connect_db(); cur = conn.cursor()
        cur.execute("""
            UPDATE khachhang
               SET tenkh=?, loaikh=?, diachi=?, sdt=?
             WHERE makh=?
        """, (tenkh, loaikh, diachi, sdt, makh))
        conn.commit()
        cur.close(); conn.close()

        self.entry_ma_kh.config(state="normal")
        self.load_data()
        self.xoatext()
    

   
    def xoa_kh(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Chưa chọn", "Hãy chọn khách hàng để xóa")
            return
        makh = self.tree.item(sel)["values"][0]
        if messagebox.askyesno("Xác nhận", f"Xóa khách hàng {makh}?"):
            conn = self.connect_db(); cur = conn.cursor()
            cur.execute("DELETE FROM khachhang WHERE makh=?", (makh,))
            conn.commit()
            cur.close(); conn.close()
            self.load_data()

    def tim_kiem(self):
        kw = self.entry_tim_kiem.get().strip()
        for i in self.tree.get_children():
            self.tree.delete(i)
        sql = "SELECT makh, tenkh, loaikh, diachi, sdt FROM khachhang"
        params = ()
        if kw:
            sql += " WHERE tenkh LIKE ? ORDER BY makh DESC"
            params = (f"%{kw}%",)
        else:
            sql += " ORDER BY makh DESC"
        conn = self.connect_db(); cur = conn.cursor()
        cur.execute(sql, params)
        for row in cur.fetchall():
            self.tree.insert("", tk.END, values=row)
        cur.close()
        conn.close()

    


if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()       
    QLKhachHang(root)
    root.mainloop()

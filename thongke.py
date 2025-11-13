import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import mysql.connector
from datetime import date, datetime
from connectdb import connect_db


# # ====== Kết nối DB ======
# def connect_db():
#     return mysql.connector.connect(
#         host="localhost",
#         user="root",
#         password="123456",
#         database="qltnd"
#     )

# ====== Canh giữa ======
def center_window(win, w=900, h=650):
    ws = win.winfo_screenwidth()
    hs = win.winfo_screenheight()
    x = (ws // 2) - (w // 2)
    y = (hs // 2) - (h // 2)
    win.geometry(f"{w}x{h}+{x}+{y}")

class FrmThongKe(tk.Toplevel):
    def __init__(self, parent=None, connect_func=connect_db):
        super().__init__(parent)
        self.connect_db = connect_func

        self.title("QUẢN LÝ CỬA HÀNG MUA BÁN THUỐC NÔNG DƯỢC")
        center_window(self, 900, 700)
        self.resizable(False, False)

        # ====== Tiêu đề ======
        lbl_title = tk.Label(self, text="THỐNG KÊ NHẬP XUẤT - LÃI LỖ - HÀNG TỒN",
                             font=("Arial", 16, "bold"))
        lbl_title.pack(pady=10)

        # ====== Khung chọn ngày ======
        frm_top = tk.Frame(self)
        frm_top.pack(padx=10, pady=5, fill="x")

        tk.Label(frm_top, text="Từ ngày:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.de_from = DateEntry(frm_top, date_pattern="yyyy-mm-dd", width=12)
        self.de_from.set_date(date.today().replace(day=1))  # mặc định đầu tháng
        self.de_from.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        tk.Label(frm_top, text="Đến ngày:").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.de_to = DateEntry(frm_top, date_pattern="yyyy-mm-dd", width=12)
        self.de_to.set_date(date.today())
        self.de_to.grid(row=0, column=3, padx=5, pady=5, sticky="w")

        tk.Button(frm_top, text="Thống kê", width=12, command=self.thong_ke).grid(row=0, column=4, padx=10)
        tk.Button(frm_top, text="Đóng", width=10, command=self.destroy).grid(row=0, column=5, padx=5)

        # ====== Khung kết quả tổng ======
        frm_sum = tk.LabelFrame(self, text="Tổng hợp")
        frm_sum.pack(padx=10, pady=5, fill="x")

        tk.Label(frm_sum, text="Tổng nhập:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.e_tong_nhap = tk.Entry(frm_sum, width=18)
        self.e_tong_nhap.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        tk.Label(frm_sum, text="Tổng bán:").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.e_tong_ban = tk.Entry(frm_sum, width=18)
        self.e_tong_ban.grid(row=0, column=3, padx=5, pady=5, sticky="w")

        tk.Label(frm_sum, text="Lãi (Bán - Nhập):").grid(row=0, column=4, padx=5, pady=5, sticky="w")
        self.e_lai = tk.Entry(frm_sum, width=18)
        self.e_lai.grid(row=0, column=5, padx=5, pady=5, sticky="w")

        # ====== Bảng hàng tồn ======
        tk.Label(self, text="HÀNG TỒN THEO SẢN PHẨM", font=("Arial", 11, "bold")).pack(padx=10, pady=(10, 0), anchor="w")

        cols = ("masp", "tensp", "slnhap", "slxuat", "slton")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", height=15)
        self.tree.heading("masp", text="Mã SP")
        self.tree.heading("tensp", text="Tên sản phẩm")
        self.tree.heading("slnhap", text="SL nhập")
        self.tree.heading("slxuat", text="SL bán")
        self.tree.heading("slton", text="SL tồn")

        self.tree.column("masp", width=80, anchor="center")
        self.tree.column("tensp", width=220)
        self.tree.column("slnhap", width=80, anchor="e")
        self.tree.column("slxuat", width=80, anchor="e")
        self.tree.column("slton", width=80, anchor="e")

        self.tree.pack(padx=10, pady=5, fill="both", expand=True)

        # chạy lần đầu
        self.thong_ke()
        self.grab_set()

    def thong_ke(self):
        # lấy khoảng ngày
        tu_ngayhd = self.de_from.get_date()
        den_ngayhd = self.de_to.get_date()
        # chuyển sang string yyyy-mm-dd
        s_from = tu_ngayhd.strftime("%Y-%m-%d")
        s_to   = den_ngayhd.strftime("%Y-%m-%d")

        conn = self.connect_db()
        cur = conn.cursor()

        # ====== 1. Tổng nhập ======
      
        cur.execute("""
            SELECT COALESCE(SUM(tongtien), 0)
            FROM hoadonmua_ct
            WHERE ngayhd BETWEEN ? AND ?
        """, (s_from, s_to))
        tong_nhap = cur.fetchone()[0] or 0

        # ====== 2. Tổng bán ======
        cur.execute("""
            SELECT COALESCE(SUM(tongtien), 0)
            FROM hoadonban_ct
            WHERE ngayhd BETWEEN ? AND ?
        """, (s_from, s_to))
        tong_ban = cur.fetchone()[0] or 0

        # ====== 3. Hàng tồn ======
        # lấy SL nhập theo sản phẩm
        cur.execute("""
            SELECT sp.masp, sp.tensp,
                   COALESCE(SUM(mua.soluong), 0) AS sl_nhap
            FROM sanpham sp
            LEFT JOIN hoadonmua_ct mua
                   ON sp.masp = mua.masp AND mua.ngayhd BETWEEN ? AND ?
            GROUP BY sp.masp, sp.tensp
            ORDER BY sp.masp
        """, (s_from, s_to))
        nhap_rows = cur.fetchall()

        # lấy SL bán theo sản phẩm
        cur.execute("""
            SELECT sp.masp,
                   COALESCE(SUM(ban.soluong), 0) AS sl_ban
            FROM sanpham sp
            LEFT JOIN hoadonban_ct ban
                   ON sp.masp = ban.masp AND ban.ngayhd BETWEEN ? AND ?
            GROUP BY sp.masp
            ORDER BY sp.masp
        """, (s_from, s_to))
        ban_rows = cur.fetchall()

        conn.close()

        # chuyển bán_rows thành dict để tra nhanh
        ban_dict = {r[0]: r[1] for r in ban_rows}

        # clear tree
        for i in self.tree.get_children():
            self.tree.delete(i)

        for masp, tensp, slnhap in nhap_rows:
            slban = ban_dict.get(masp, 0)
            slton = (slnhap or 0) - (slban or 0)
            self.tree.insert("", tk.END, values=(masp, tensp, slnhap, slban, slton))

       # điền các ô tổng
        self.e_tong_nhap.delete(0, tk.END)
        self.e_tong_nhap.insert(0, f"{tong_nhap:,.0f}")

        self.e_tong_ban.delete(0, tk.END)
        self.e_tong_ban.insert(0, f"{tong_ban:,.0f}")

        lai = tong_ban - tong_nhap
        self.e_lai.delete(0, tk.END)
        self.e_lai.insert(0, f"{lai:,.0f}")


if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    FrmThongKe(root)
    root.mainloop()

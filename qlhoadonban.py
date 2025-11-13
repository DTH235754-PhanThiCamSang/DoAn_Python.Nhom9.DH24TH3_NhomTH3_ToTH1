import tkinter as tk 
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import mysql.connector
from datetime import date
from connectdb import connect_db
# ====== Kết nối DB ======
# def connect_db():
#     return mysql.connector.connect(
#         host="localhost",
#         user="root",
#         password="123456",
#         database="qltnd"
#     )

def center_window(win, w=900, h=700):
    ws = win.winfo_screenwidth()
    hs = win.winfo_screenheight()
    x = (ws // 2) - (w // 2)
    y = (hs // 2) - (h // 2)
    win.geometry(f"{w}x{h}+{x}+{y}")

def money(s: str) -> float:
    s = s.strip().replace(",", "")
    try:
        return float(s) if s else 0.0
    except:
        return 0.0

# ====== Tạo số hóa đơn tự động ======
def sohd():
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT MAX(sohd) FROM hoadonban_ct WHERE sohd LIKE 'HDB%'")
    row = cur.fetchone()
    conn.close()
    num = int(row[0][3:]) + 1 if row and row[0] else 1
    return f"HDB{num:03d}"

# ====== Form hóa đơn bán ======
class FrmHoaDonBan(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("QUẢN LÝ CỬA HÀNG MUA BÁN THUỐC NÔNG DƯỢC")
        self.resizable(False, False)
        center_window(self, 900, 700)

        # dict lưu masp -> tensp
        self.masp_to_tensp = {}

        tk.Label(self, text="QUẢN LÝ HÓA ĐƠN BÁN", font=("Arial", 16, "bold")).pack(pady=10)
        self.TaoUI()

    # ====== Load danh sách mã KH ======
    def load_khachhang(self):
        conn = connect_db()
        cur = conn.cursor()
        cur.execute("SELECT makh FROM khachhang ORDER BY makh")
        rows = [r[0] for r in cur.fetchall()]
        conn.close()
        self.cbb_kh["values"] = rows
        if rows:
            self.cbb_kh.current(0)

    # ====== Load danh sách MÃ SP từ bảng sanpham cho combobox ======
    def load_sanpham(self):
        conn = connect_db()
        cur = conn.cursor()
        cur.execute("SELECT masp, tensp FROM sanpham ORDER BY masp")
        rows = cur.fetchall()
        conn.close()

        masp_list = []
        self.masp_to_tensp = {}
        for masp, tensp in rows:
            masp_list.append(masp)
            self.masp_to_tensp[masp] = tensp

        self.cbb_masp["values"] = masp_list
        if masp_list:
            self.cbb_masp.current(0)
            # set tên SP tương ứng với masp đầu tiên
            first = masp_list[0]
            self.e_tensp.delete(0, tk.END)
            self.e_tensp.insert(0, self.masp_to_tensp.get(first, ""))

    def TaoUI(self):
        # ==== Thông tin chung ====
        f_top = tk.LabelFrame(self, text="Thông tin chung")
        f_top.pack(fill="x", padx=10, pady=5)

        tk.Label(f_top, text="Số hóa đơn").grid(row=0, column=0, padx=5, pady=4)
        self.e_sohd = tk.Entry(f_top, width=15)
        self.e_sohd.grid(row=0, column=1, padx=5, pady=4)

        tk.Label(f_top, text="Ngày").grid(row=0, column=2, padx=5, pady=4)
        self.e_ngayhd = DateEntry(f_top, width=12, date_pattern="yyyy-mm-dd")
        self.e_ngayhd.set_date(date.today())
        self.e_ngayhd.grid(row=0, column=3, padx=5, pady=4)

        # === Combobox KH ===
        tk.Label(f_top, text="Mã khách hàng").grid(row=0, column=4, padx=5, pady=4)
        self.cbb_kh = ttk.Combobox(f_top, width=15, state="readonly")
        self.cbb_kh.grid(row=0, column=5, padx=5, pady=4)

        # ==== Khu nhập hàng ====
        f_in = tk.LabelFrame(self, text="Thêm mặt hàng")
        f_in.pack(fill="x", padx=10, pady=5)

        tk.Label(f_in, text="Mã SP").grid(row=0, column=0)
        # ---- COMBOBOX MÃ SP ----
        self.cbb_masp = ttk.Combobox(f_in, width=12, state="readonly")
        self.cbb_masp.grid(row=0, column=1, padx=5, pady=4)
        self.cbb_masp.bind("<<ComboboxSelected>>", self.on_masp_selected)

        tk.Label(f_in, text="Tên SP").grid(row=0, column=2)
        self.e_tensp = tk.Entry(f_in, width=20)
        self.e_tensp.grid(row=0, column=3, padx=5, pady=4)

        tk.Label(f_in, text="SL").grid(row=0, column=4)
        self.e_sl = tk.Entry(f_in, width=5, justify="right")
        self.e_sl.insert(0, "1")
        self.e_sl.grid(row=0, column=5, padx=5)

        tk.Label(f_in, text="Đơn giá").grid(row=0, column=6)
        self.e_dg = tk.Entry(f_in, width=10, justify="right")
        self.e_dg.grid(row=0, column=7, padx=5)

        tk.Button(f_in, text="Thêm dòng", command=self.them_dong).grid(row=0, column=8, padx=5)
        tk.Button(f_in, text="Xóa dòng", command=self.xoa_dong).grid(row=0, column=9, padx=5)

        # ==== Treeview ====
        cols = ("sohd", "ngayhd", "makh", "masp", "tensp", "soluong", "dongia", "thanhtien")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", height=12)
        headers = ["Số HĐ", "Ngày", "Mã KH", "Mã SP", "Tên SP", "SL", "Đơn giá", "Thành tiền"]
        for c, t in zip(cols, headers):
            self.tree.heading(c, text=t)
        for c in cols:
            self.tree.column(c, width=100)
        self.tree.pack(fill="both", padx=10, pady=5, expand=True)

        # ==== Tổng + nút ====
        f_bot = tk.Frame(self)
        f_bot.pack(fill="x", padx=10, pady=5)
        self.lbl_tong = tk.Label(f_bot, text="Tổng tiền: 0 VND", font=("Arial", 12, "bold"))
        self.lbl_tong.pack(side="left")

        tk.Button(f_bot, text="Lưu hóa đơn", command=self.luu_data).pack(side="right", padx=4)
        tk.Button(f_bot, text="Hóa đơn mới", command=self.hoa_don_moi).pack(side="right", padx=4)
        tk.Button(f_bot, text="Tải HĐ", command=self.load_all_invoices).pack(side="right", padx=4)
        tk.Button(f_bot, text="Thoát", command=self.destroy).pack(side="right", padx=4)

        # load dữ liệu cho 2 combobox + tree
        self.load_khachhang()
        self.load_sanpham()
        self.load_all_invoices()

    # ===== Khi chọn MÃ SP thì tự hiện TÊN SP =====
    def on_masp_selected(self, event=None):
        masp = self.cbb_masp.get().strip()
        tensp = self.masp_to_tensp.get(masp, "")
        self.e_tensp.delete(0, tk.END)
        self.e_tensp.insert(0, tensp)

    # ==== Thêm dòng ====
    def them_dong(self):
        sohd = self.e_sohd.get().strip()
        ngayhd = self.e_ngayhd.get_date().strftime("%Y-%m-%d")
        makh = self.cbb_kh.get().strip()

        masp = self.cbb_masp.get().strip().upper()
        tensp = self.e_tensp.get().strip()
        try:
            sl = int(self.e_sl.get().strip())
        except:
            sl = 0
        dg = money(self.e_dg.get())

        if not masp or sl <= 0:
            messagebox.showwarning("Thiếu dữ liệu", "Mã SP và SL > 0")
            return
        if not makh:
            messagebox.showwarning("Thiếu dữ liệu", "Chưa chọn khách hàng")
            return

        thanhtien = sl * dg
        self.tree.insert("", tk.END, values=(sohd, ngayhd, makh, masp, tensp, sl, dg, thanhtien))
        self.tong_tien()

        # reset dòng nhập
        self.cbb_masp.set("")
        self.e_tensp.delete(0, tk.END)
        self.e_sl.delete(0, tk.END); self.e_sl.insert(0, "1")
        self.e_dg.delete(0, tk.END)

    # ==== Xóa dòng ====
    def xoa_dong(self):
        for iid in self.tree.selection():
            self.tree.delete(iid)
        self.tong_tien()

    # ==== Tổng tiền ====
    def tong_tien(self):
        total = 0
        for iid in self.tree.get_children():
            total += float(self.tree.item(iid)["values"][7])
        self.lbl_tong.config(text=f"Tổng tiền: {total:,.0f} VND")
        return total

    # ==== Load tất cả HĐ ====
    def load_all_invoices(self):
        for iid in self.tree.get_children():
            self.tree.delete(iid)
        conn = connect_db()
        cur = conn.cursor()
        cur.execute("""
            SELECT sohd, ngayhd, makh, masp, tensp, soluong, dongia, thanhtien, tongtien
            FROM hoadonban_ct ORDER BY sohd
        """)
        for row in cur.fetchall():
            self.tree.insert("", tk.END, values=row[:-1])
        conn.close()
        self.tong_tien()

    # ==== Lưu dữ liệu ====
    def luu_data(self):
        sohd = self.e_sohd.get().strip()
        if not sohd:
            messagebox.showwarning("Thiếu", "Chưa có số hóa đơn"); return
        if not self.tree.get_children():
            messagebox.showwarning("Thiếu", "Chưa có mặt hàng"); return

        tong = self.tong_tien()
        conn = connect_db()
        cur = conn.cursor()
        try:
            for iid in self.tree.get_children():
                sohd, ngayhd, makh, masp, tensp, sl, dg, tt = self.tree.item(iid)["values"]
                cur.execute("""
                    INSERT INTO hoadonban_ct
                    (sohd, ngayhd, makh, masp, tensp, soluong, dongia, thanhtien, tongtien)
                    VALUES (?,?,?,?,?,?,?,?,?)
                """, (sohd, ngayhd, makh, masp, tensp, int(sl), float(dg), float(tt), float(tong)))
            conn.commit()
            messagebox.showinfo("OK", "Đã lưu hóa đơn thành công.")
        except Exception as e:
            conn.rollback()
            messagebox.showerror("Lỗi", str(e))
        finally:
            conn.close()

    def hoa_don_moi(self):
        self.e_sohd.delete(0, tk.END)
        self.e_sohd.insert(0, sohd())
        self.e_ngayhd.set_date(date.today())
        for iid in self.tree.get_children():
            self.tree.delete(iid)
        self.tong_tien()


if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    FrmHoaDonBan(root)
    root.mainloop()

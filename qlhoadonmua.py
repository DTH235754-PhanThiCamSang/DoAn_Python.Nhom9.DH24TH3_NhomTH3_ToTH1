import tkinter as tk 
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import mysql.connector
from datetime import datetime, date
from connectdb import connect_db

# ====== Kết nối DB ======
# def connect_db():
#     return mysql.connector.connect(
#         host="localhost",
#         user="root",
#         password="123456",
#         database="qltnd"
#     )

# ====== Hàm canh giữa cửa sổ ======
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

# ====== Tạo số hóa đơn dạng HDM001 từ DB ======
def sohd():
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT MAX(sohd)
        FROM hoadonmua_ct
        WHERE sohd LIKE 'HDM%'
    """)
    row = cur.fetchone()
    conn.close()

    if row and row[0]:
        last_code = row[0]
        num = int(last_code[3:]) + 1
    else:
        num = 1

    return f"HDM{num:03d}"


class FrmHoaDonMua(tk.Toplevel):
    def __init__(self, parent=None, connect_db_func=connect_db):
        super().__init__(parent)

        self.title("QUẢN LÝ CỬA HÀNG MUA BÁN THUỐC NÔNG DƯỢC")
        self.resizable(False, False)
        center_window(self, 900, 700)

        self.connect_db = connect_db_func
        self.masp_to_tensp = {}   # lưu mapping masp -> tensp

        # ===== TIÊU ĐỀ =====
        lbl_title = tk.Label(self, text="QUẢN LÝ HÓA ĐƠN MUA",
                             font=("Arial", 16, "bold"))
        lbl_title.pack(pady=10)

        # ===== Thông tin chung =====
        f_top = tk.LabelFrame(self, text="Thông tin chung")
        f_top.pack(fill="x", padx=10, pady=5)

        tk.Label(f_top, text="Số hóa đơn").grid(row=0, column=0, padx=5, pady=4, sticky="w")
        self.e_sohd = tk.Entry(f_top, width=25)
        self.e_sohd.grid(row=0, column=1, padx=5, pady=4, sticky="w")

        tk.Label(f_top, text="Ngày nhập").grid(row=0, column=2, padx=5, pady=4, sticky="w")
        self.e_ngay = DateEntry(f_top, width=15, date_pattern="yyyy-mm-dd")
        self.e_ngay.set_date(date.today())
        self.e_ngay.grid(row=0, column=3, padx=5, pady=4, sticky="w")

        tk.Label(f_top, text="Mã NCC").grid(row=0, column=4, padx=5, pady=5, sticky="w")
        self.cbb_mancc = ttk.Combobox(f_top, width=35, state="readonly")
        self.cbb_mancc.grid(row=0, column=5, padx=5, pady=5, sticky="w")

        # gọi để đổ dữ liệu từ bảng nhacungcap
        self.load_mancc_to_combo()

        # ===== Nhập dòng =====
        f_in = tk.LabelFrame(self, text="Thêm mặt hàng nhập")
        f_in.pack(fill="x", padx=10, pady=5)

        tk.Label(f_in, text="Mã SP").grid(row=0, column=0, padx=5, pady=4)
        # COMBOBOX MÃ SP
        self.cbb_masp = ttk.Combobox(f_in, width=12, state="readonly")
        self.cbb_masp.grid(row=0, column=1, padx=5, pady=4)

        tk.Label(f_in, text="Tên SP").grid(row=0, column=2, padx=5, pady=4)
        self.e_tensp = tk.Entry(f_in, width=20)
        self.e_tensp.grid(row=0, column=3, padx=5, pady=4)

        tk.Label(f_in, text="SL").grid(row=0, column=4, padx=5, pady=4)
        self.e_sl = tk.Entry(f_in, width=5, justify="right")
        self.e_sl.insert(0, "1")
        self.e_sl.grid(row=0, column=5, padx=5, pady=4)

        tk.Label(f_in, text="Đơn giá nhập").grid(row=0, column=6, padx=5, pady=4)
        self.e_dg = tk.Entry(f_in, width=10, justify="right")
        self.e_dg.grid(row=0, column=7, padx=5, pady=4)

        tk.Button(f_in, text="Thêm dòng", width=10, command=self.them_dong).grid(row=0, column=10, padx=8)
        tk.Button(f_in, text="Xóa dòng", width=8, command=self.xoa_dong).grid(row=0, column=11, padx=4)

        # ===== Bảng =====
        cols = ("sohd", "ngayhd", "mancc", "masp", "tensp", "soluong", "dongia", "thanhtien")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", height=12)
        for c, t in zip(cols, ["Số HĐ Mua", "Ngày HĐ", " Mã Nhà cung cấp", "Mã SP", "Tên Sản Phẩm",
                               "Số lượng", "Đơn giá nhập", "Thành tiền"]):
            self.tree.heading(c, text=t)
        self.tree.column("sohd", width=80)
        self.tree.column("ngayhd", width=90)
        self.tree.column("mancc", width=180)
        self.tree.column("masp", width=80)
        self.tree.column("tensp", width=160)
        self.tree.column("soluong", width=60, anchor="e")
        self.tree.column("dongia", width=90, anchor="e")
        self.tree.column("thanhtien", width=100, anchor="e")
        self.tree.pack(fill="both", padx=10, pady=5, expand=True)

        # ===== Tổng + nút =====
        f_bot = tk.Frame(self)
        f_bot.pack(fill="x", padx=10, pady=5)
        self.lbl_tong = tk.Label(f_bot, text="Tổng tiền nhập: 0 VND", font=("Arial", 12, "bold"))
        self.lbl_tong.pack(side="left")

        tk.Button(f_bot, text="Lưu phiếu nhập", width=14, command=self.luu_data).pack(side="right", padx=4)
        tk.Button(f_bot, text="Phiếu nhập mới", width=14, command=self.new_invoice).pack(side="right", padx=4)
        tk.Button(f_bot, text="Tải tất cả HĐ", width=12, command=self.load_all_invoices).pack(side="right", padx=4)
        tk.Button(f_bot, text="Thoát", width=10, command=self.destroy).pack(side="right", padx=4)

        # load masp và gắn sự kiện chọn
        self.load_masp_to_combo()
        self.cbb_masp.bind("<<ComboboxSelected>>", self.on_masp_selected)

        self.load_all_invoices()

    # ====== chức năng ======
    def load_mancc_to_combo(self):
        try:
            conn = connect_db()
            cur = conn.cursor()
            cur.execute("SELECT mancc FROM nhacungcap ORDER BY mancc")
            rows = cur.fetchall()
            conn.close()

            names = [r[0] for r in rows]
            self.cbb_mancc["values"] = names
            if names:
                self.cbb_mancc.current(0)
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không tải được danh sách NCC\n{e}")

    def load_masp_to_combo(self):
       
        try:
            conn = connect_db()
            cur = conn.cursor()
            cur.execute("SELECT masp, tensp FROM sanpham ORDER BY masp")
            rows = cur.fetchall()
            conn.close()

            ds_masp = []
            self.masp_to_tensp = {}
            for masp, tensp in rows:
                ds_masp.append(masp)
                self.masp_to_tensp[masp] = tensp

            self.cbb_masp["values"] = ds_masp
            if ds_masp:
                self.cbb_masp.current(0)
                # set tên SP tương ứng cho masp đầu tiên
                first = ds_masp[0]
                self.e_tensp.delete(0, tk.END)
                self.e_tensp.insert(0, self.masp_to_tensp.get(first, ""))
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không tải được danh sách Mã SP\n{e}")
# """Khi chọn mã SP, tự hiển thị tên SP tương ứng"""
    def on_masp_selected(self, event=None):
       
        masp = self.cbb_masp.get().strip()
        tensp = self.masp_to_tensp.get(masp, "")
        self.e_tensp.delete(0, tk.END)
        self.e_tensp.insert(0, tensp)

    def them_dong(self):
        sohd = self.e_sohd.get().strip()
        ngayhd = self.e_ngay.get_date().strftime("%Y-%m-%d")
        mancc = self.cbb_mancc.get().strip()

        # Mã SP lấy từ combobox
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

        thanhtien = sl * dg
        self.tree.insert("", tk.END, values=(sohd, ngayhd, mancc, masp, tensp, sl, dg, thanhtien))
        self.tong_tien()

       
        
        self.cbb_masp.set("")
        self.e_sl.delete(0, tk.END); self.e_sl.insert(0, "1")
        self.e_dg.delete(0, tk.END)
        self.cbb_masp.focus_set()
        

    def xoa_dong(self):
        for iid in self.tree.selection():
            self.tree.delete(iid)
        self.tong_tien()

    # Tải toàn bộ dữ liệu trong bảng hoadonmua_ct lên TreeView 
    def load_all_invoices(self):
        for iid in self.tree.get_children():
            self.tree.delete(iid)

        conn = connect_db()
        cur = conn.cursor()
        cur.execute("""
            SELECT sohd, ngayhd, mancc, masp, tensp, soluong, dongia, thanhtien
            FROM hoadonmua_ct
            ORDER BY sohd, masp
        """)
        rows = cur.fetchall()
        conn.close()

        total_all = 0
        for sohd, ngayhd, mancc, masp, tensp, sl, dg, tt in rows:
            self.tree.insert("", tk.END, values=(sohd, ngayhd, mancc, masp, tensp, sl, dg, tt))
            total_all += float(tt or 0)

        self.lbl_tong.config(text=f"Tổng tiền (tất cả): {total_all:,.0f} VND")

    def tong_tien(self):
        total = 0.0
        for iid in self.tree.get_children():
            row = self.tree.item(iid)["values"]
            total += float(row[7])
        self.lbl_tong.config(text=f"Tổng tiền nhập: {total:,.00f} VND")
        return total

    def luu_data(self):
        sohd = self.e_sohd.get().strip()
        ngayhd = self.e_ngay.get()
        mancc = self.cbb_mancc.get().strip()
        if not sohd:
            messagebox.showwarning("Thiếu dữ liệu", "Chưa có số hóa đơn hoặc mã sản phẩm")
            return
        if not self.tree.get_children():
            messagebox.showwarning("Thiếu dữ liệu", "Chưa có dòng hàng")
            return

        tongtien = self.tong_tien()
        conn = connect_db()
        cur = conn.cursor()

        try:
            first = True
            for iid in self.tree.get_children():
                sohd, ngayhd, mancc, masp, tensp, sl, dg, tt = self.tree.item(iid)["values"]

                if first:
                    cur.execute("""
                        INSERT INTO hoadonmua_ct
                            (sohd, ngayhd, masp, tensp, mancc, soluong, dongia, thanhtien, tongtien)
                        VALUES (?,?,?,?,?,?,?,?,?)
                    """, (sohd, ngayhd, masp, tensp, mancc,
                          int(sl), float(dg), float(tt), float(tongtien)))
                    first = False
                else:
                    cur.execute("""
                        INSERT INTO hoadonmua_ct
                            (sohd, ngayhd, masp, tensp, mancc, soluong, dongia, thanhtien, tongtien)
                        VALUES (?,?,?,?,?,?,?,?,?)
                    """, (sohd, ngayhd, masp, tensp, mancc,
                          int(sl), float(dg), float(tt), None))

            conn.commit()
            messagebox.showinfo("OK",
                                f"Đã lưu {len(self.tree.get_children())} dòng cho phiếu nhập {sohd}")
            self.new_invoice(clear=False)
        except Exception as e:
            conn.rollback()
            messagebox.showerror("Lỗi", str(e))
        finally:
            conn.close()

    def new_invoice(self, clear=True):
        self.e_sohd.delete(0, tk.END)
        self.e_sohd.insert(0, sohd())
        self.e_ngay.set_date(date.today())
        self.load_mancc_to_combo()

        for iid in self.tree.get_children():
            self.tree.delete(iid)
        self.tong_tien()

        if clear:
            messagebox.showinfo("Thông báo", "Bạn có thể nhập phiếu nhập mới.")

        # reset dòng nhập
        self.cbb_masp.set("")
        self.e_tensp.delete(0, tk.END)
        self.e_sl.delete(0, tk.END); self.e_sl.insert(0, "1")
        self.e_dg.delete(0, tk.END)
        self.cbb_masp.focus_set()


if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    FrmHoaDonMua(root)
    root.mainloop()

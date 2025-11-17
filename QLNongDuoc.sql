-- ============================================
-- TẠO CƠ SỞ DỮ LIỆU QLNongDuoc
-- ============================================
DROP DATABASE QLNongDuoc;
GO

IF EXISTS (SELECT name FROM sys.databases WHERE name = N'QLNongDuoc')
BEGIN
    ALTER DATABASE QLNongDuoc SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
    DROP DATABASE QLNongDuoc;
END
GO

CREATE DATABASE QLNongDuoc
ON 
(
    NAME = QLNongDuoc_mdf, 
    FILENAME = 'D:\CNTT\NAM3\NAM3_HK1\Python\QLNongDuoc.mdf',  
    SIZE = 15MB, 
    MAXSIZE = 50MB, 
    FILEGROWTH = 5MB
)
LOG ON
(
    NAME = QLNongDuoc_log, 
    FILENAME = 'D:\CNTT\NAM3\NAM3_HK1\Python\QLNongDuoc.ldf',  
    SIZE = 15MB, 
    MAXSIZE = 50MB, 
    FILEGROWTH = 5MB
);
GO

USE QLNongDuoc;
GO

-- Xóa bảng cũ theo thứ tự quan hệ (bảng con trước)
IF OBJECT_ID('hoadonban_ct', 'U') IS NOT NULL DROP TABLE hoadonban_ct;
IF OBJECT_ID('hoadonmua_ct', 'U') IS NOT NULL DROP TABLE hoadonmua_ct;
IF OBJECT_ID('sanpham', 'U') IS NOT NULL DROP TABLE sanpham;
IF OBJECT_ID('khachhang', 'U') IS NOT NULL DROP TABLE khachhang;
IF OBJECT_ID('nhacungcap', 'U') IS NOT NULL DROP TABLE nhacungcap;
IF OBJECT_ID('users', 'U') IS NOT NULL DROP TABLE users;
GO


CREATE TABLE nhacungcap (
    mancc NVARCHAR(6) PRIMARY KEY,
    tenncc NVARCHAR(200) NOT NULL,
    diachi NVARCHAR(255),
    sodienthoai NVARCHAR(15),
    email NVARCHAR(150)
);

CREATE TABLE sanpham (
    masp   NVARCHAR(6)   PRIMARY KEY,
    tensp  NVARCHAR(255) NOT NULL,
    loaisp NVARCHAR(100),
    dvt    NVARCHAR(50),
    giaban DECIMAL(12,2),
    hsd    DATE,
    mancc  NVARCHAR(6),

    CONSTRAINT sanpham_fk_mancc
        FOREIGN KEY (mancc)
        REFERENCES nhacungcap(mancc)
);


-- KHÁCH HÀNG
CREATE TABLE khachhang (
    makh NVARCHAR(6) PRIMARY KEY,
    tenkh NVARCHAR(255) NOT NULL,
    loaikh NVARCHAR(100),
    diachi NVARCHAR(255),
    sdt NVARCHAR(15) NOT NULL
);

CREATE TABLE hoadonmua_ct (
    sohd       NVARCHAR(6)   NOT NULL,
    ngayhd     DATE          NOT NULL,
    mancc      NVARCHAR(6)   NOT NULL,
    masp       NVARCHAR(6)   NOT NULL,
    tensp      NVARCHAR(255) NOT NULL,
    soluong    INT           NOT NULL,
    dongia     DECIMAL(14,2) NOT NULL,
    thanhtien  DECIMAL(14,2) NOT NULL,
    tongtien   DECIMAL(14,2),

    PRIMARY KEY (sohd, masp),

    CONSTRAINT hoadonmua_ct_fk_masp
        FOREIGN KEY (masp)
        REFERENCES sanpham(masp),

    CONSTRAINT hoadonmua_ct_fk_mancc
        FOREIGN KEY (mancc)
        REFERENCES nhacungcap(mancc)
       
);

CREATE TABLE hoadonban_ct (
    sohd      NVARCHAR(6)  NOT NULL,
    ngayhd    DATE         NOT NULL,
    makh      NVARCHAR(6)  NOT NULL,
    masp      NVARCHAR(6)  NOT NULL,
    tensp     NVARCHAR(255) NOT NULL,
    soluong   INT          NOT NULL,
    dongia    DECIMAL(14,2) NOT NULL,
    thanhtien DECIMAL(14,2) NOT NULL,
    tongtien  DECIMAL(14,2),
    PRIMARY KEY (sohd, masp),
    CONSTRAINT hoadonban_ct_fk_masp FOREIGN KEY (masp) REFERENCES sanpham(masp),
       
    CONSTRAINT hoadonban_ct_fk_makh FOREIGN KEY (makh) REFERENCES khachhang(makh)
       
);


-- USERS
CREATE TABLE users (
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(128) NOT NULL,
    full_name NVARCHAR(100),
    security_question NVARCHAR(255),
    security_answer_hash VARCHAR(128)
);



-- ============================================
-- KIỂM TRA DỮ LIỆU
-- ============================================

SELECT * FROM nhacungcap;
SELECT * FROM sanpham;
SELECT * FROM khachhang;
SELECT * FROM hoadonmua_ct;
SELECT * FROM hoadonban_ct;
SELECT * FROM users;
GO


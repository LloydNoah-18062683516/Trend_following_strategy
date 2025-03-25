SHOW DATABASES;
-- 查看允许导入文件的目录
SHOW VARIABLES LIKE 'secure_file_priv';
CREATE DATABASE stock_db;
USE stock_db;

-- 在MySQL中创建表（字段需与CSV列对应）
CREATE TABLE maotai_stock (
    trade_date DATE PRIMARY KEY,
    open DECIMAL(10,2),
    high DECIMAL(10,2),
    low DECIMAL(10,2),
    close DECIMAL(10,2)
);

-- 或 Windows路径
LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/maotai_2020-2024.csv'
INTO TABLE maotai_stock
FIELDS TERMINATED BY ','  
ENCLOSED BY '"'
LINES TERMINATED BY '\n' 
IGNORE 1 ROWS
(trade_date, open, high, low, close);

SELECT * FROM maotai_stock;

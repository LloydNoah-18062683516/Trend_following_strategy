SHOW DATABASES;
USE stock_db;
SELECT * FROM maotai_stock;

CREATE TABLE strategy_status (
    id INT AUTO_INCREMENT PRIMARY KEY,
    strategy_name VARCHAR(255) NOT NULL,
    last_trade_date DATE COMMENT '最后处理的交易日',
    current_position INT DEFAULT 0 COMMENT '当前持仓方向(1:多仓, -1:空仓, 0:空仓)',
    last_signal INT DEFAULT 0 COMMENT '最后生成的信号',
    params JSON COMMENT '策略参数存储',
    update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY (strategy_name)
);
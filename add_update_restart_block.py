import mysql.connector
import pandas as pd
import json
import time
from datetime import datetime
import plotly.graph_objs as go
from plotly.subplots import make_subplots


class StockDB:
    def __init__(self):
        self.conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Ljj2006080302@",
            database="stock_db"
        )

    def fetch_data(self):
        query = "SELECT trade_date, close FROM maotai_stock ORDER BY trade_date"
        df = pd.read_sql(query, self.conn)
        return df.set_index('trade_date')

    def close(self):
        self.conn.close()


class StrategyStateManager:
    def __init__(self, strategy_name="maotai_ma_strategy"):
        self.strategy_name = strategy_name
        self.conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Ljj2006080302@",
            database="stock_db"
        )
        self._init_table()

    def _init_table(self):
        cursor = self.conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS strategy_status (
            id INT AUTO_INCREMENT PRIMARY KEY,
            strategy_name VARCHAR(255) NOT NULL,
            last_trade_date DATE,
            current_position INT DEFAULT 0,
            last_signal INT DEFAULT 0,
            params JSON,
            update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            UNIQUE KEY (strategy_name)
        )
        """)
        self.conn.commit()
        cursor.close()

    # 修改save_state方法，添加类型转换
    def save_state(self, last_date, position, signal, params=None):
        cursor = self.conn.cursor()
        query = """
        INSERT INTO strategy_status 
            (strategy_name, last_trade_date, current_position, last_signal, params)
        VALUES (%s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            last_trade_date = VALUES(last_trade_date),
            current_position = VALUES(current_position),
            last_signal = VALUES(last_signal),
            params = VALUES(params)
        """
        # 转换numpy类型为Python原生类型
        if hasattr(position, 'item'):  # 检查是否是numpy类型
            position = position.item()
        if hasattr(signal, 'item'):
            signal = signal.item()

        cursor.execute(query, (
            self.strategy_name,
            last_date,
            int(position),  
            int(signal),
            json.dumps(params) if params else None
        ))
        self.conn.commit()
        cursor.close()

    def load_state(self):
        cursor = self.conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM strategy_status WHERE strategy_name = %s",
                       (self.strategy_name,))
        result = cursor.fetchone()
        cursor.close()
        return result

    def close(self):
        self.conn.close()


def generate_signals(df):
    df['5_ma'] = df['close'].rolling(5).mean()
    df['20_ma'] = df['close'].rolling(20).mean()
    df['signal'] = 0
    df.loc[df['5_ma'] > df['20_ma'], 'signal'] = 1
    df.loc[df['5_ma'] < df['20_ma'], 'signal'] = -1
    return df


class RealtimeVisualizer:
    def __init__(self):
        self.fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            subplot_titles=["价格与均线", "信号分布"],
            vertical_spacing=0.15
        )

    def update_plot(self, df):
        self.fig.data = []

        # 价格和均线
        self.fig.add_trace(go.Scatter(
            x=df.index, y=df['close'], name='收盘价', line=dict(color='blue')
        ), row=1, col=1)
        self.fig.add_trace(go.Scatter(
            x=df.index, y=df['5_ma'], name='5日均线', line=dict(color='orange')
        ), row=1, col=1)
        self.fig.add_trace(go.Scatter(
            x=df.index, y=df['20_ma'], name='20日均线', line=dict(color='green')
        ), row=1, col=1)

        # 信号标记
        buy_signals = df[df['signal'] == 1]
        sell_signals = df[df['signal'] == -1]
        self.fig.add_trace(go.Scatter(
            x=buy_signals.index, y=buy_signals['close'],
            mode='markers', name='买入', marker=dict(color='green', size=10)
        ), row=1, col=1)
        self.fig.add_trace(go.Scatter(
            x=sell_signals.index, y=sell_signals['close'],
            mode='markers', name='卖出', marker=dict(color='red', size=10)
        ), row=1, col=1)

        self.fig.update_layout(
            title='茅台股价均线策略实时监控',
            hovermode="x unified",
            height=800
        )
        self.fig.show()


if __name__ == "__main__":
    db = StockDB()
    state_mgr = StrategyStateManager()
    visualizer = RealtimeVisualizer()

    # 加载上次状态
    saved_state = state_mgr.load_state()
    last_position = saved_state['current_position'] if saved_state else 0
    last_date = saved_state['last_trade_date'].strftime('%Y-%m-%d') if saved_state else None

    try:
        while True:
            df = db.fetch_data()
            df = generate_signals(df)

            latest_signal = df['signal'].iloc[-1]
            latest_date = df.index[-1].strftime('%Y-%m-%d')

            # 状态保存逻辑（产生新信号时保存）
            if latest_signal != 0 and (not saved_state or latest_date != last_date):
                state_mgr.save_state(
                    last_date=latest_date,
                    position=latest_signal,
                    signal=latest_signal,
                    params={'window_short': 5, 'window_long': 20}
                )
                last_position = latest_signal
                last_date = latest_date

            # 可视化最近60个交易日
            visualizer.update_plot(df.tail(60))
            time.sleep(10)

    except KeyboardInterrupt:
        # 确保退出前保存最终状态
        if 'df' in locals():
            state_mgr.save_state(
                last_date=df.index[-1].strftime('%Y-%m-%d'),
                position=last_position,
                signal=df['signal'].iloc[-1]
            )
        db.close()
        state_mgr.close()

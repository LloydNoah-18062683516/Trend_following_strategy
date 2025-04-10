# 数据库交互模块
import mysql.connector
import pandas as pd


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


# 均线策略逻辑
def generate_signals(df):
    # 计算均线
    df['5_ma'] = df['close'].rolling(5).mean()
    df['20_ma'] = df['close'].rolling(20).mean()

    # 生成信号（1:买入，-1:卖出）
    df['signal'] = 0
    df.loc[df['5_ma'] > df['20_ma'], 'signal'] = 1
    df.loc[df['5_ma'] < df['20_ma'], 'signal'] = -1
    return df


# 可视化
import plotly.graph_objs as go
from plotly.subplots import make_subplots


class RealtimeVisualizer:
    def __init__(self):
        self.fig = make_subplots(
            rows=2,
            cols=1,
            shared_xaxes=True,  # 正确参数名
            subplot_titles=["价格与均线", "信号分布"],  # 子图标题[1](@ref)
            vertical_spacing=0.15
        )

    def update_plot(self, df):
        # 清除旧数据
        self.fig.data = []

        # 绘制价格和均线
        self.fig.add_trace(go.Scatter(
            x=df.index, y=df['close'], name='收盘价', line=dict(color='blue')
        ), row=1, col=1)
        self.fig.add_trace(go.Scatter(
            x=df.index, y=df['5_ma'], name='5日均线', line=dict(color='orange')
        ), row=1, col=1)
        self.fig.add_trace(go.Scatter(
            x=df.index, y=df['20_ma'], name='20日均线', line=dict(color='green')
        ), row=1, col=1)

        # 绘制信号
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

        # 更新布局
        self.fig.update_layout(
            title='茅台股价跟随策略实时监控',
            hovermode="x unified",
            height=800
        )
        self.fig.show()

# 主函数
import time

if __name__ == "__main__":
    db = StockDB()
    visualizer = RealtimeVisualizer()

    while True:
        try:
            # 获取最新数据
            df = db.fetch_data()
            df = generate_signals(df)

            # 更新可视化
            visualizer.update_plot(df.tail(60))  # 显示最近60个交易日

            # 间隔10秒刷新
            time.sleep(10)

        except KeyboardInterrupt:
            db.close()
            break

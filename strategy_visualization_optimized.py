# 数据库交互模块
import mysql.connector
import pandas as pd

class StockDB:
    def __init__(self):
        self.conn = mysql.connector.connect(
            host="localhost", user="root", password="Ljj2006080302@", database="stock_db"
        )

    def fetch_annual_data(self, year):
        query = f"""
            SELECT trade_date, close 
            FROM maotai_stock 
            WHERE YEAR(trade_date) = {year}
            ORDER BY trade_date
        """
        df = pd.read_sql(query, self.conn)
        return df.set_index('trade_date')

    def close(self):
        self.conn.close()


# 均线策略逻辑
import numpy as np
def generate_annual_signals(df):
    df['5_ma'] = df['close'].rolling(5).mean()
    df['20_ma'] = df['close'].rolling(20).mean()
    df['signal'] = np.where(df['5_ma'] > df['20_ma'], 1, -1)
    return df


#可视化
import plotly.graph_objs as go
from plotly.subplots import make_subplots
class AnnualReportVisualizer:
    @staticmethod
    def generate_annual_plot(df, year):
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                            subplot_titles=[f"{year}年价格与信号", "成交量分布"])

        # 价格与均线
        fig.add_trace(go.Scatter(x=df.index, y=df['close'], name='收盘价'), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['5_ma'], name='5日均线'), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['20_ma'], name='20日均线'), row=1, col=1)

        # 信号标记
        buy_signals = df[df['signal'] == 1]
        sell_signals = df[df['signal'] == -1]
        fig.add_trace(go.Scatter(x=buy_signals.index, y=buy_signals['close'],
                                 mode='markers', name='买入'), row=1, col=1)
        fig.add_trace(go.Scatter(x=sell_signals.index, y=sell_signals['close'],
                                 mode='markers', name='卖出'), row=1, col=1)

        # 输出到HTML文件
        fig.write_html(f"maotai_{year}_strategy_report.html")
        print(f"已生成{year}年度报告: maotai_{year}_strategy_report.html")

# 主函数
import time

if __name__ == "__main__":
    db = StockDB()
    visualizer = AnnualReportVisualizer()

    # 生成2019-2024各年度报告
    for year in range(2020, 2025):
        try:
            annual_df = db.fetch_annual_data(year)
            if not annual_df.empty:
                processed_df = generate_annual_signals(annual_df)
                visualizer.generate_annual_plot(processed_df, year)
            else:
                print(f"警告: {year}年无数据")
        except Exception as e:
            print(f"{year}年数据处理失败: {str(e)}")

    db.close()

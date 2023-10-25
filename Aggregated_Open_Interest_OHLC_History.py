# Aggregated_Open_Interest_OHLC_History.py

from flask import Blueprint, render_template, request
import requests
from datetime import datetime

chart_blueprint = Blueprint('Aggregated_Open_Interest_OHLC_History', __name__)

# 获取真实未平仓合约数据
def get_real_chart_data(symbol, interval, data_points):
    url = f"https://open-api.coinglass.com/public/v2/indicator/open_interest_aggregated_ohlc?symbol={symbol}&interval={interval}"
    headers = {
        "accept": "application/json",
        "coinglassSecret": "c3115385695f4af9b5b5e657216899c9"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()["data"][-data_points:]  # 取最近 data_points 个数据
        # 提取时间和未平仓合约数据，并将时间戳转换为可读时间格式
        labels = [datetime.fromtimestamp(item["t"] / 1000).strftime('%Y-%m-%d %H:%M:%S') for item in data]
        values = [item["c"] for item in data]
        return {"labels": labels, "values": values}
    else:
        return {"error": "无法获取数据"}

@chart_blueprint.route('/')
def chart():
    # 获取币种、时间周期和数据点数量参数
    symbol = request.args.get('symbol', 'BTC')
    interval = request.args.get('interval', 'h1')
    data_points = int(request.args.get('dataPoints', 24))  # 默认为24个数据点
    # 获取真实数据
    chart_data = get_real_chart_data(symbol, interval, data_points)
    return render_template('Aggregated_Open_Interest_OHLC_History.html', chart_data=chart_data, symbol=symbol, interval=interval, dataPoints=data_points)

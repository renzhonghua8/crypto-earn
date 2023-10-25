from flask import Flask, render_template, request, jsonify, Blueprint
import requests
import matplotlib.pyplot as plt
import datetime
from io import BytesIO
import base64

chart_blueprint = Blueprint('Open_Interest_History', __name__)

# 默认参数值
DEFAULT_SYMBOL = "BTC"
DEFAULT_TIME_TYPE = "h1"
DEFAULT_CURRENCY = "USDT"
DEFAULT_THRESHOLD = 5  # 默认的差异阈值

def generate_plots(symbol, time_type, currency, threshold):
    # 根据用户输入的参数构建API请求
    url = f"https://open-api.coinglass.com/public/v2/open_interest_history"
    params = {
        "symbol": symbol,
        "time_type": time_type,
        "currency": currency
    }

    headers = {
        "coinglassSecret": "c3115385695f4af9b5b5e657216899c9",
        "User-Agent": "Apifox/1.0.0 (https://apifox.com)"
    }

    response = requests.get(url, params=params, headers=headers)
    data = response.json()

    # 提取数据
    dateList = data["data"]["dateList"]
    dates = [datetime.datetime.fromtimestamp(ts / 1000) for ts in dateList]
    priceList = data["data"]["priceList"]
    binanceData = data["data"]["dataMap"]["Binance"]

    # 创建两个图表，一个用于价格数据，另一个用于Binance数据
    plt.figure(figsize=(12, 6))

    # 绘制价格数据
    plt.subplot(2, 1, 1)
    plt.plot(dates, priceList, label="Price", marker='o', linestyle='-', markersize=2)
    plt.xlabel("Date")
    plt.ylabel("Price")
    plt.title("Price Over Time")
    plt.grid(True)

    # 绘制Binance数据的折线图，根据原先的变色逻辑绘制线
    plt.subplot(2, 1, 2)
    condition_flags = []

    for i in range(5, len(binanceData)):
        data_slice = [binanceData[i - j] for j in range(1, 6)]

        # 检查数据是否有效，如果有None值，将标志设为False
        valid_data = all(d is not None for d in data_slice)

        if valid_data:
            diff_percent = [(data_slice[j - 1] - data_slice[j]) / data_slice[j] * 100 for j in range(1, 5)]

            # 判断是否有任何两个数据之间的差异大于等于用户设置的阈值
            condition_met = any(abs(d) >= threshold for d in diff_percent)
        else:
            condition_met = False

        # 添加到标志列表中
        condition_flags.append(condition_met)

        if condition_flags[i - 5]:
            if binanceData[i] < binanceData[i - 1]:
                color = 'black'
            else:
                color = 'red'
        else:
            color = 'green'
        plt.plot(dates[i], binanceData[i], color=color, marker='o', linestyle='-', linewidth=2, markersize=6, label="Binance Data")

    plt.xlabel("Date")
    plt.ylabel("Binance Data")
    plt.title("Binance Data Over Time")
    plt.grid(True)

    # 将绘图保存到字节流
    img = BytesIO()
    plt.tight_layout()
    plt.savefig(img, format='png')
    img.seek(0)
    plots_data = base64.b64encode(img.getvalue()).decode()

    return plots_data

@chart_blueprint.route('/', methods=['GET', 'POST'])
def show_plots():
    if request.method == 'POST':
        # 获取用户输入的参数
        symbol = request.form.get('symbol', DEFAULT_SYMBOL)
        time_type = request.form.get('time_type', DEFAULT_TIME_TYPE)
        currency = request.form.get('currency', DEFAULT_CURRENCY)
        threshold = float(request.form.get('threshold', DEFAULT_THRESHOLD))
        plots_data = generate_plots(symbol, time_type, currency, threshold)
    else:
        # 如果是GET请求，初始化参数为默认值
        symbol = DEFAULT_SYMBOL
        time_type = DEFAULT_TIME_TYPE
        currency = DEFAULT_CURRENCY
        threshold = DEFAULT_THRESHOLD
        plots_data = None

    return render_template('Open_Interest_History.html', plots_data=plots_data, symbol=symbol, time_type=time_type, currency=currency, threshold=threshold)



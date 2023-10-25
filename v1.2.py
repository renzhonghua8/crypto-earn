from flask import Flask, render_template, request, jsonify
import requests
import matplotlib.pyplot as plt
import datetime
from io import BytesIO
import base64

app = Flask(__name__)

# 默认参数值
DEFAULT_SYMBOL = "BTC"
DEFAULT_TIME_TYPE = "h1"
DEFAULT_CURRENCY = "USDT"
DEFAULT_THRESHOLD = 5  # 默认的差异阈值


def longshortratio(symbol, time_type):
    # 根据用户输入的参数构建API请求
    url = f"https://open-api.coinglass.com/public/v2/long_short_history?time_type={time_type}&symbol={symbol}"
    headers = {
        "accept": "application/json",
        "coinglassSecret": "c3115385695f4af9b5b5e657216899c9"
    }
    response = requests.get(url, headers=headers)
    data = response.json()

    # 提取数据
    date_list = data['data']['dateList']
    price_list = data['data']['priceList']
    long_short_rate_list = data['data']['longShortRateList']

    # 转换时间戳为真实时间
    real_time_list = [datetime.datetime.fromtimestamp(timestamp / 1000) for timestamp in date_list]

    # 创建两子图
    fig, ax1 = plt.subplots(figsize=(12, 6))

    # 绘制价格和多空比率折线图
    ax1.plot(real_time_list, price_list, label='price', marker='o')
    ax1.set_ylabel('price')
    ax1.set_title('Price and Long-Short Ratio')
    ax1.grid(True)
    ax1.legend()

    # 创建第二个坐标轴用于多空比率
    ax2 = ax1.twinx()
    ax2.plot(real_time_list, long_short_rate_list, label='ratio', marker='o', color='g')
    ax2.axhline(1, color='r', linestyle='--', label='1')
    ax2.set_ylabel('ratio')
    ax2.legend()

    plt.xticks(rotation=45)

    # 将绘图保存到字节流
    img = BytesIO()
    plt.tight_layout()
    plt.savefig(img, format='png')
    img.seek(0)
    plots_data = base64.b64encode(img.getvalue()).decode()

    return plots_data


@app.route('/api/get_data', methods=['GET'])
def get_data():
    symbol = request.args.get('symbol', DEFAULT_SYMBOL)
    time_type = request.args.get('time_type', DEFAULT_TIME_TYPE)
    plots_data = longshortratio(symbol, time_type)
    return jsonify({"plots_data": plots_data})


@app.route('/', methods=['GET', 'POST'])
def show_plots():
    if request.method == 'POST':
        # 获取用户输入的参数
        symbol = request.form.get('symbol', DEFAULT_SYMBOL)
        time_type = request.form.get('time_type', DEFAULT_TIME_TYPE)
        plots_data = longshortratio(symbol, time_type)
    else:
        # 如果是GET请求，初始化参数为默认值
        symbol = DEFAULT_SYMBOL
        time_type = DEFAULT_TIME_TYPE
        plots_data = None

    return render_template('Open_Interest_History.html', plots_data=plots_data, symbol=symbol, time_type=time_type)


if __name__ == '__main__':
    app.run(debug=True, port=5001)

import time

from flask import Flask, render_template, request, jsonify, Blueprint
import requests
import matplotlib.pyplot as plt
import datetime
from io import BytesIO
import base64
from itertools import islice

app = Flask(__name__)
chart_blueprint = Blueprint('Open_Interest_History', __name__)

# 默认参数值
DEFAULT_SYMBOL = "BTC"
DEFAULT_TIME_TYPE = "h1"
DEFAULT_CURRENCY = "USDT"
DEFAULT_THRESHOLD = 1

def batch(iterable, size):
    iterator = iter(iterable)
    while True:
        batch = list(islice(iterator, size))
        if not batch:
            break
        yield batch

def generate_plot(symbol, time_type, currency, threshold):
    try:
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

        # 检查API响应是否包含 'data' 键
        if 'data' in data:
            dateList = data["data"].get("dateList", [])
            dates = [datetime.datetime.fromtimestamp(ts / 1000) for ts in dateList]
            priceList = data["data"].get("priceList", [])
            data_map = data["data"].get("dataMap", {})

            if 'Binance' in data_map:
                binanceData = data_map['Binance']
                # ...[处理Binance数据和绘图逻辑]...
            else:
                print("Binance data not available")
                return None
        else:
            print(f"数据不可用或发生错误: {symbol}")
            return None, None  # 确保返回的是一个元组
        if not priceList or not binanceData:
            return None, None
        # 创建两个图表
        plt.figure(figsize=(12, 6))

        # 绘制价格数据
        plt.subplot(2, 1, 1)
        plt.plot(dates, priceList, label="Price", marker='o', linestyle='-', markersize=2)
        plt.xlabel("")
        plt.ylabel("Price")
        plt.title(f"Price Over Time for {symbol}")
        plt.grid(True)

        # 绘制Binance数据的折线图
        plt.subplot(2, 1, 2)
        condition_flags = []

        for i in range(5, len(binanceData)):
            data_slice = [binanceData[i - j] for j in range(1, 6)]

            # 检查数据是否有效，如果有None值，将标志设为False
            valid_data = all(d is not None for d in data_slice)

            if valid_data:
                diff_percent = [(data_slice[j - 1] - data_slice[j]) / data_slice[j] * 100 for j in range(1, 5)]
                condition_met = any(abs(d) >= threshold for d in diff_percent)
            else:
                condition_met = False

            condition_flags.append(condition_met)

            if condition_flags[i - 5]:
                color = 'black' if binanceData[i] < binanceData[i - 1] else 'red'
            else:
                color = 'green'

            plt.plot(dates[i], binanceData[i], color=color, marker='o', linestyle='-', linewidth=2, markersize=6)

        plt.xlabel("")
        plt.ylabel("Data")
        plt.title(f"Open Interest Over Time for {symbol}")
        plt.grid(True)

        # 将绘图保存到字节流
        img = BytesIO()
        plt.tight_layout()
        plt.savefig(img, format='png')
        img.seek(0)
        plot_data = base64.b64encode(img.getvalue()).decode()
        plt.close()

        # Calculate statistics
        statistics = {
            'max_price': max(priceList) if priceList else None,
            'min_price': min(priceList) if priceList else None,
            'max_data': max(binanceData) if binanceData else None,
            'min_data': min(binanceData) if binanceData else None,
            'price_change': ((priceList[-1] - priceList[0]) / priceList[0] * 100) if len(priceList) > 1 else None,
            'data_change': ((binanceData[-1] - binanceData[0]) / binanceData[0] * 100) if len(binanceData) > 1 else None,
        }

        return plot_data, statistics
    except Exception as error:
        # 当出现异常时，打印错误并返回两个None
        print(f"Error in generate_plot: {error}")
        return None, None


def generate_multiple_plots(symbols, time_type, currency, threshold):
    plots_data = {}
    statistics_list = {}
    # 分批处理每次15个symbols
    for batch_symbols in batch(symbols, 15):
        for symbol in batch_symbols:
            plot_data, stats = generate_plot(symbol, time_type, currency, threshold)
            # 确保plot_data和stats不是None，然后再进行下一步处理
            if plot_data is not None and stats is not None:
                plots_data[symbol] = plot_data
                statistics_list[symbol] = stats
            else:
                # 处理这个symbol因为错误没有数据的情况
                print(f"跳过 {symbol}，因为没有生成数据。")
        time.sleep(60)
    return plots_data, statistics_list


@chart_blueprint.route('/', methods=['GET', 'POST'])
def show_plots():
    plots_data = None
    statistics_list = None

    if request.method == 'POST':
        symbol = request.form.get('symbol', DEFAULT_SYMBOL)
        time_type = request.form.get('time_type', DEFAULT_TIME_TYPE)
        currency = request.form.get('currency', DEFAULT_CURRENCY)
        threshold = float(request.form.get('threshold', DEFAULT_THRESHOLD))

        if 'generate_multiple' in request.form:
            symbols = [
                "1000FLOKI", "1000LUNC", "1000PEPE", "1000SHIB", "1000XEC", "1INCH", "AAVE", "ACH", "ADA", "AGIX",
                "AGLD", "ALGO", "ALICE", "ALPHA", "AMB", "ANKR", "ANT", "APE", "API3", "APT",
                "ARB", "ARKM", "ARK", "ARPA", "AR", "ASTR", "ATA", "ATOM", "AUDIO", "AVAX",
                "AXS", "BAKE", "BAL", "BAND", "BAT", "BCH", "BEL", "BICO", "BIGTIME", "BLUEBIRD",
                "BLUR", "BLZ", "BNB", "BNT", "BNX", "BOND", "BSV", "BTC", "C98", "CAKE",
                "CELO", "CELR", "CFX", "CHR", "CHZ", "CKB", "COMBO", "COMP", "COTI", "CRV",
                "CTK", "CTSI", "CVX", "CYBER", "DAR", "DASH", "DEFI", "DENT", "DGB", "DODOX",
                "DOGE", "DOT", "DUSK", "DYDX", "EDU", "EGLD", "ENJ", "ENS", "EOS", "ETC",
                "ETH", "FET", "FIL", "FLM", "FLOW", "FOOTBALL", "FRONT", "FTM", "FXS", "GALA",
                "GAL", "GAS", "GLMR", "GMT", "GMX", "GRT", "GTC", "HBAR", "HFT", "HIFI",
                "HIGH", "HOOK", "HOT", "ICP", "ICX", "IDEX", "ID", "IMX", "INJ", "IOST",
                "IOTA", "IOTX", "JASMY", "JOE", "KAVA", "KEY", "KLAY", "KNC", "KSM", "LDO",
                "LEVER", "LINA", "LINK", "LIT","LOOM", "LPT", "LQTY", "LRC", "LTC", "LUNA2", "MAGIC",
                "MANA", "MASK", "MATIC", "MAV", "MDT", "MEME", "MINA", "MKR", "MTL", "NEAR",
                "NEO", "NKN", "NMR", "OCEAN", "OGN", "OMG", "ONE", "ONT", "OP", "ORBS",
                "OXT", "PENDLE", "PEOPLE", "PERP", "PHB", "POLYX", "POWR", "QNT", "QTUM", "RAD",
                "RDNT", "REEF", "REN", "RIF", "RLC", "RNDR", "ROSE", "RSR", "RUNE", "RVN",
                "SAND", "SEI", "SFP", "SKL", "SLP", "SNT", "SNX", "SOL", "SPELL", "SSV",
                "STG", "STMX", "STORJ", "STPT", "STRAX", "STX", "SUI", "SUSHI", "SXP", "THETA",
                "TIA", "TLM", "TOKEN", "TOMO", "TRB", "TRU", "TRX", "TU", "TWT", "UMA",
                "UNFI", "UNI", "VET", "WAVES", "WAXP", "WLD", "WOO", "XEM", "XLM", "XMR",
                "XRP", "XTZ", "XVG", "XVS", "YFI", "YGG", "ZEC", "ZEN", "ZIL", "ZRX"
            ]
            plots_data, statistics_list = generate_multiple_plots(symbols, time_type, currency, threshold)

            # 在发送到前端之前，按 data_change 对数据进行排序
            sorted_items = sorted(statistics_list.items(), key=lambda item: item[1]['data_change'] if item[1]['data_change'] is not None else -float('inf'), reverse=True)
            # 创建新的排序后的字典
            sorted_statistics_list = {k: v for k, v in sorted_items}
            sorted_plots_data = {k: plots_data[k] for k, _ in sorted_items}
            plots_data = sorted_plots_data
            statistics_list = sorted_statistics_list

        else:
            plot_data, stats = generate_plot(symbol, time_type, currency, threshold)
            if plot_data and stats:
                plots_data = {symbol: plot_data}
                statistics_list = {symbol: stats}
                # 单个项目不需要排序
            else:
                # 处理无数据情况
                plots_data = {}
                statistics_list = {}

    return render_template('Open_Interest_History.html', plots_data=plots_data, statistics_list=statistics_list)
def calculate_statistics(data):
    # 假设 `data` 是一个包含所有需要计算统计信息的列表
    max_data = max(data)
    min_data = min(data)
    data_change = ((max_data - min_data) / min_data * 100) if min_data != 0 else 0
    return {
        'max_data': max_data,
        'min_data': min_data,
        'data_change': data_change
    }





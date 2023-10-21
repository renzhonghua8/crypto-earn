import requests
import matplotlib.pyplot as plt
import datetime

# 发送HTTP GET请求
url = "https://open-api.coinglass.com/public/v2/open_interest_history"
params = {
    "symbol": "AGLD",
    "time_type": "h1",
    "currency": "USDT"
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

# 创建上图表，显示价格数据
plt.figure(figsize=(12, 6))
plt.plot(dates, priceList, label="Price", marker='o', linestyle='-', markersize=2)
plt.xlabel("Date")
plt.ylabel("Price")
plt.title("Price Over Time")
plt.legend()
plt.grid(True)

# 创建下图表，显示Binance数据
plt.figure(figsize=(12, 6))
plt.plot(dates, binanceData, label="Binance", marker='o', linestyle='-', markersize=2, color='orange')
plt.xlabel("Date")
plt.ylabel("Binance Data")
plt.title("Binance Data Over Time")
plt.legend()
plt.grid(True)
# 判断相邻的5个数据是否有任何两个数据之间的差异大于等于--%
# 创建一个列表，用于存储是否满足条件的标志
condition_flags = []

# 遍历数据，检查相邻的5个数据是否满足条件
for i in range(5, len(binanceData)):
    data_slice = [binanceData[i - j] for j in range(1, 6)]

    # 检查数据是否有效，如果有None值，将标志设为False
    valid_data = all(d is not None for d in data_slice)

    if valid_data:
        diff_percent = [(data_slice[j - 1] - data_slice[j]) / data_slice[j] * 100 for j in range(1, 5)]

        # 判断是否有任何两个数据之间的差异大于等于5%
        condition_met = any(abs(d) >= 5 for d in diff_percent)
    else:
        condition_met = False

    # 添加到标志列表中
    condition_flags.append(condition_met)

# 遍历数据并根据条件绘制散点图
for i in range(5, len(binanceData)):
    if condition_flags[i - 5]:
        if binanceData[i] < binanceData[i - 1]:
            plt.scatter(dates[i], binanceData[i], color='black', s=60, label="Any >= 5% and Decreasing")
        else:
            plt.scatter(dates[i], binanceData[i], color='red', s=30, label="Any >= 5%")
    else:
        plt.scatter(dates[i], binanceData[i], color='green', s=30, label="None >= 5%")

plt.xlabel("Date")
plt.ylabel("Binance Data")
plt.title("Binance Data Over Time")
plt.legend()
plt.grid(True)

# 显示图表
plt.xticks(rotation=45)  # 旋转x轴标签以提高可读性
plt.tight_layout()
plt.show()
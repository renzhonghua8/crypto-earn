import requests
import matplotlib.pyplot as plt
from datetime import datetime

# 发送请求获取数据
url = "https://open-api.coinglass.com/public/v2/long_short_history?time_type=h1&symbol=AGLD"
headers = {
    "accept": "application/json",
    "coinglassSecret": "c3115385695f4af9b5b5e657216899c9"
}
response = requests.get(url, headers=headers)
data = response.json()

# 解析数据
date_list = data['data']['dateList']
price_list = data['data']['priceList']
long_short_rate_list = data['data']['longShortRateList']

# 转换时间戳为真实时间
real_time_list = [datetime.fromtimestamp(timestamp / 1000) for timestamp in date_list]

# 创建两子图
fig, ax1 = plt.subplots(figsize=(12, 6))

# 绘制价格和多空比率折线图
ax1.plot(real_time_list, price_list, label='price', marker='o')
ax1.set_ylabel('price')
ax1.set_title('price and longshortratio')
ax1.grid(True)
ax1.legend()

# 创建第二个坐标轴用于多空比率
ax2 = ax1.twinx()
ax2.plot(real_time_list, long_short_rate_list, label='ratio', marker='o', color='g')
ax2.axhline(1, color='r', linestyle='--', label='1')
ax2.set_ylabel('ratio')
ax2.legend()

plt.xticks(rotation=45)  # 旋转x轴标签，使其更易阅读

plt.show()

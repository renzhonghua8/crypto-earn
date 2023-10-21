import requests

url = "https://open-api.coinglass.com/public/v2/liquidation_top?time_type=h4"

headers = {
    "accept": "application/json",
    "coinglassSecret": "c3115385695f4af9b5b5e657216899c9"
}

response = requests.get(url, headers=headers)

print(response.text)
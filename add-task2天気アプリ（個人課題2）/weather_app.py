import requests

# ① 地域一覧を取得
area_url = "http://www.jma.go.jp/bosai/common/const/area.json"
area_data = requests.get(area_url).json()

centers = area_data["centers"]

print("地域一覧（コード : 地域名）")
for code, info in centers.items():
    print(code, ":", info["name"])

# ② 地域コードを入力
area_code = input("\n天気を見たい地域コードを入力してください: ")

# ③ 天気予報を取得
forecast_url = f"https://www.jma.go.jp/bosai/forecast/data/forecast/{area_code}.json"
forecast_data = requests.get(forecast_url).json()

forecast = forecast_data[0]
area = forecast["timeSeries"][0]["areas"][0]

# ④ 天気を表示
print("\n地域:", area["area"]["name"])
print("今日の天気:", area["weathers"][0])
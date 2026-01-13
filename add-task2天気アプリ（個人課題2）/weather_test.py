import requests

area_code = "130000"  # 東京

url = f"https://www.jma.go.jp/bosai/forecast/data/forecast/{area_code}.json"

response = requests.get(url)
data = response.json()

forecast = data[0]
area = forecast["timeSeries"][0]["areas"][0]

print("地域:", area["area"]["name"])
print("今日の天気:", area["weathers"][0])
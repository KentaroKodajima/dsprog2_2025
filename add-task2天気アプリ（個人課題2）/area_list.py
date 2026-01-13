import requests

url = "http://www.jma.go.jp/bosai/common/const/area.json"

response = requests.get(url)
data = response.json()

# 中身のキーを確認
print(data.keys())

centers = data["centers"]

for code, info in centers.items():
    print(code, info["name"])
    break
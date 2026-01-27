from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import re
from bs4 import BeautifulSoup
import sqlite3   # ★ 追加

SEARCH = "https://jrechien.com/?s=%E5%9F%BC%E4%BA%AC%E5%B7%9D%E8%B6%8A%E7%B7%9A"
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
wait = WebDriverWait(driver, 10)

# ----------------------
# タイトル解析
# ----------------------
def parse_title(title):
    section_match = re.search(r"\[(.+?)\]", title)
    section = section_match.group(1) if section_match else None

    time_match = re.search(r"（(.+?)現在", title)
    date, time_ = None, None
    if time_match:
        dt = time_match.group(1)
        m = re.match(r"(\d+月\d+日)(\d+時\d+分)", dt)
        if m:
            date = m.group(1)
            time_ = m.group(2)

    return section, date, time_

# ----------------------
# 本文解析
# ----------------------
def parse_content(content_tag):
    station = None
    cause = None
    status = None

    if not content_tag:
        return station, cause, status

    for p in content_tag.find_all("p"):
        text = p.get_text()

        text = re.sub(r".+?(線内での|駅での|駅間での)", "", text)

        if not station:
            m = re.search(r"([^\s、。]+駅)", text)
            if m:
                station = m.group(1)

        if not status:
            if "運転を見合わせ" in text:
                status = "運転見合わせ"
            elif "遅れ" in text or "遅延" in text:
                status = "遅延"
            elif "平常通り" in text:
                status = "平常運転"

        if not cause:
            m = re.search(r"(.+?)の影響", text)
            if m:
                cause = m.group(1)

    return station, cause, status

# ----------------------
# メイン処理
# ----------------------
all_data = []
page = 1
valid_keyword = "埼京川越線"

while True:
    print(f"--- Page {page} ---")
    driver.get(SEARCH + f"&paged={page}")
    wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    time.sleep(1)

    soup = BeautifulSoup(driver.page_source, "html.parser")

    sidebar = soup.find("div", id="sidebar")
    if sidebar:
        sidebar.decompose()

    links = list(set(re.findall(
        r"https://jrechien\.com/delay/\d{4}-\d{2}-\d{2}/\?p=\d+",
        str(soup)
    )))

    if not links:
        print("No more pages. END.")
        break

    print(f"Found {len(links)} links.")

    for link in links:
        driver.get(link)
        time.sleep(1)

        soup = BeautifulSoup(driver.page_source, "html.parser")
        title_tag = soup.select_one("h1.entry-title")
        content_tag = soup.select_one("div.entry-content")

        if not title_tag:
            continue

        title = title_tag.get_text(strip=True)

        if valid_keyword not in title:
            continue

        section, date, time_ = parse_title(title)
        station, cause, status = parse_content(content_tag)

        all_data.append({
            "title": title,
            "section": section,
            "date": date,
            "time": time_,
            "station": station,
            "cause": cause,
            "status": status,
            "url": link
        })

    page += 1
    time.sleep(1)

driver.quit()

# ----------------------
# SQLite保存（★ CSVの代わり）
# ----------------------
conn = sqlite3.connect("jr_delay_saikyo.db")
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS delays (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    section TEXT,
    date TEXT,
    time TEXT,
    station TEXT,
    cause TEXT,
    status TEXT,
    url TEXT
)
""")

for row in all_data:
    cur.execute("""
    INSERT INTO delays (
        title, section, date, time,
        station, cause, status, url
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        row["title"],
        row["section"],
        row["date"],
        row["time"],
        row["station"],
        row["cause"],
        row["status"],
        row["url"]
    ))

conn.commit()
conn.close()

print(f"Saved {len(all_data)} records → jr_delay_saikyo.db (SQLite)")
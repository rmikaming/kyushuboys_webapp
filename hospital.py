import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time
from database import init_hospital_db, sync_hospitals

#クローリング実行
def get_hospitals():

    hospitals = []

#病院サイトの1ページ目から2ページ目を検索
    page = 1
    while True:
#    for page in range(1,3):
        if page == 1:
            url = "https://byoinnavi.jp/nagasaki/isahayashi"
        else:
            url = f"https://byoinnavi.jp/nagasaki/isahayashi?p={page}"

        r = requests.get(url)
        html = r.text
        soup = BeautifulSoup(html, "html.parser")

#病院名と住所を抽出
        names = soup.select("div.corp-name a")
        addresses = soup.select("div.corp-address")

#名前が見つからなくなったら終了
        if not names:
            break

#1ページに複数ある病院名、住所を順番にhospitalのリストに格納
        for name, address in zip(names, addresses):
            hospitals.append({
                "name":name.get_text(strip=True),
                "address":address.contents[0].strip(),
                "created_at":datetime.now().isoformat()
            })

        page += 1
        time.sleep(1)

    return hospitals

#hospitalテーブル作成とクローリング、データ削除・登録実行
def update_hospital_db():
    init_hospital_db()
    hospitals = get_hospitals()
    sync_hospitals(hospitals)
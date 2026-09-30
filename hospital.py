import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time

def get_hospitals():

    hospitals = []

#病院サイトの1ページ目から2ページ目を検索
    for page in range(1,3):
        if page == 1:
            url = "https://byoinnavi.jp/nagasaki"
        else:
            url = f"https://byoinnavi.jp/nagasaki?p={page}"

        r = requests.get(url)
        html = r.text
        soup = BeautifulSoup(html, "html.parser")

#病院名と住所を抽出
        names = soup.select("div.corp-name a")
        addresses = soup.select("div.corp-address")

#1ページに複数ある病院名、住所を順番にhospitalのリストに格納
        for name, address in zip(names, addresses):
            hospitals.append({
                "name":name.get_text(strip=True),
                "address":address.contents[0].strip(),
                "created_at":datetime.now().isoformat()
            })

        time.sleep(1)

    return hospitals

print(get_hospitals())





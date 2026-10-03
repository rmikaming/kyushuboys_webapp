from hospital import get_hospitals
from database import init_db, sync_hospitals

init_db()

hospitals = get_hospitals()

sync_hospitals(hospitals)

print("保存完了")
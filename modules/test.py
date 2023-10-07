from datetime import datetime
from zoneinfo import ZoneInfo
import locale

locale.setlocale(locale.LC_TIME, 'ja_JP.UTF-8')
origin_tz = ZoneInfo("Asia/Tokyo")
txt = "1/2(水)"

result = datetime.strptime(txt, "%m/%d(%a)").replace(tzinfo=origin_tz,year=2023,month=2)
raw = result.strftime("%Y年%m月%d日(%a) %H:%M %Z")
print(raw)

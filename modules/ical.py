from icalendar import Event
import base64,datetime,zoneinfo
from modules.dataclass import GradeRace, LocationName
from modules.locations import LOCATIONS_INFO

BASE_URL="https://jra.jp/keiba"
COMMON_URL=f"{BASE_URL}/common"
ORIGIN_TZ=zoneinfo.ZoneInfo("Asia/Tokyo")

def get_x_apple_structured_location(race_course: LocationName):
    infoset = LOCATIONS_INFO[race_course]
    return {
        'name': "X-APPLE-STRUCTURED-LOCATION",
        'value': f"geo:{infoset.geo}",
        'parameters': {
            "VALUE": "URI",
            'X-APPLE-REFERENCEFRAME': "1",
            'X-TITLE': infoset.name,
            'X-ADDRESS': infoset.address,
        }
    }

def create_event_block(race: GradeRace):

    now = datetime.datetime.now(tz=ORIGIN_TZ)

    # UIDを作る
    raw_uid = f"{race.start_at}{race.name}"
    uid_enc = raw_uid.encode('utf-8')
    uid = base64.b64encode(uid_enc)

    # タイトルを作る（グレード表記の部分は絵文字に書き換える）
    summary = f"{race.grade.replace('J・','').replace('G1','🥇').replace('G2','🥈').replace('G3','🥉').replace('Jpn1','🥇').replace('Jpn2','🥈').replace('Jpn3','🥉')}{race.name}"

    # 競馬場の情報を取得する(X-APPLE-STRUCTURED_LOCATIONの形式に合わせる)
    x_apple_structured_location = get_x_apple_structured_location(race.festival_location)

    # 本文を作る
    urls = []
    locateinfo = LOCATIONS_INFO[race.festival_location]

    if locateinfo.flag != None:
        summary = locateinfo.flag + summary
    if race.special_url != None:
        urls.append(f"分析: {race.special_url}")
    if race.netkeiba_url != None:
        if type(race.end_at) is datetime.date:
            urls.append(f"出走: {race.netkeiba_url}")
        elif type(race.end_at) is datetime.datetime:
            if now < race.end_at:
                urls.append(f"出走: {race.netkeiba_url}")
            else:
                urls.append(f"結果: {race.netkeiba_url}")
    if race.archive_url != None:
        urls.append(f"映像: {race.archive_url}")
    if locateinfo.admission != None:
        urls.append(f"入場: {locateinfo.admission}")
    if locateinfo.reservation != None:
        urls.append(f"予約: {locateinfo.reservation}")
    if locateinfo.betting != None:
        urls.append(f"投票: {locateinfo.betting}")
    if locateinfo.live != None:
        urls.append(f"LIVE: {locateinfo.live}")
    description = "\n".join(urls)

    event = Event()
    event.add('UID', uid)
    event.add('SUMMARY', summary)
    event.add('DESCRIPTION', description)
    event.add('DTSTART', race.start_at)
    event.add('DTEND', race.end_at)
    event.add('LOCATION', f"{x_apple_structured_location['parameters']['X-TITLE']}\n{x_apple_structured_location['parameters']['X-ADDRESS']}"),
    event.add(**x_apple_structured_location)
    event.add('TRANSP', 'TRANSPARENT')
    if race.netkeiba_url != None:
        event.add('URL', race.netkeiba_url, parameters={'VALUE': 'URI'})
    return event

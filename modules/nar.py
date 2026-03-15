import datetime,locale,logging,re,unicodedata,urllib,zoneinfo
import modules.bsclient as bsc
import requests
from modules.dataclass import GradeRace, LocationName
from modules.locations import LOCATIONS_INFO
from modules.netkeiba import get_netkeiba_url

NETKEIBA_SCHEDULE_URL = "https://nar.netkeiba.com/top/schedule.html"
KEIBAGO_ROOT_URL = "https://www.keiba.go.jp"
KEIBAGO_DIRTRACE_ROOT_URL = f"{KEIBAGO_ROOT_URL}/dirtgraderace"
KEIBAGO_RACELIST_URL = "https://www.keiba.go.jp/KeibaWeb/TodayRaceInfo/RaceList"

ORIGIN_TZ = zoneinfo.ZoneInfo("Asia/Tokyo")

def get_calendar_active_years() -> list[int]:

    years:list[int] = []
    resp = requests.get(f"{KEIBAGO_DIRTRACE_ROOT_URL}/common/js/racelist.js")
    if resp.status_code != 200:
        logging.warning("failed to get race years")
        return None
    years = sorted(set(re.findall(r"20\d{2}", resp.text)))
    return years

def get_grade_races_by_year(year:int) -> list[GradeRace]:
    locale.setlocale(locale.LC_TIME, 'ja_JP.UTF-8')
    now = datetime.datetime.now(ORIGIN_TZ)
    grade_races:list[GradeRace] = []

    soup = bsc.get_soup(f"{KEIBAGO_DIRTRACE_ROOT_URL}/{year}/racelist/index.html")
    races = soup.select("div#list > div.month > ul > li.js-item")

    for race in races:
        if len(race.select("a")) > 0:
            race = race.select("a")[0]
            special_url = KEIBAGO_ROOT_URL + race.get('href').replace("racecard", "analysis")
        else:
            special_url = None

        meta = race.select("p")
        location = LocationName(meta[1].text.split(' ')[0].strip())
        meta_start_at = f"{year}年{meta[0].text.replace("祝", "").replace("振", "")}"

        if LOCATIONS_INFO[location].keibago_babacode != None:
            race_data = GradeRace(
            festival_location=location,
                name=race.select_one("h4").text.replace("ステークス", "S").replace("カップ", "C"),
                detail=race.select_one("h4").text,
                grade=race.select_one("h4").get("class")[0].capitalize(),
                start_at=datetime.datetime.strptime(meta_start_at, "%Y年%m月%d日(%a)").replace(tzinfo=ORIGIN_TZ),
                special_url=special_url,
            )
            grade_races.append(race_data)

    for race_data in grade_races:

        if (race_data.start_at - now).days < 5:
            race_data.start_at, race_data.race_number = get_start_time_and_race_number(race_data.detail, race_data.start_at, race_data.festival_location)

        # 過去のレースの場合はアーカイブURLを追加する
        if race_data.start_at.date() < now.date():
            race_data.archive_url = "https://www.youtube.com/@nar_keiba/search?query=" + urllib.parse.quote(race_data.name + " " + str(race_data.start_at.year))

        # 発走時刻が取得できた場合は5分間、それ以外は全日イベントとして定義
        if race_data.start_at.hour != 0:
            race_data.end_at = race_data.start_at + datetime.timedelta(minutes=5)
        else:
            race_data.end_at = (race_data.start_at + datetime.timedelta(days=1)).date()
            race_data.start_at = race_data.start_at.date()

        # レース番が取得できた場合はNETKEIBAのURLも定義
        if race_data.race_number != None:
            race_data.netkeiba_url = get_netkeiba_url(race_data.start_at, race_data.festival_location, race_data.race_number)

        logging.info(f"### {race_data.start_at}: {race_data.detail}")
    return grade_races

def get_start_time_and_race_number(name:str, date:datetime.datetime, location:LocationName):

    soup = bsc.get_soup("{u}?k_raceDate={y}%2f{m}%2f{d}&k_babaCode={b}".format(
        u=KEIBAGO_RACELIST_URL,
        b=LOCATIONS_INFO[location].keibago_babacode,
        y=date.strftime("%Y"),
        m=date.strftime("%m"),
        d=date.strftime("%d"),
    ))

    races = soup.select("section.raceTable > table > tbody > tr.data")

    for race in races:
        race_data = race.select("td")
        if name in unicodedata.normalize('NFKC', race_data[4].text):
            hour_str, minute_str = race_data[1].text.split(':')
            date = date.replace(hour=int(hour_str), minute=int(minute_str))
            race_number = int(race_data[0].text.replace("R", ""))
            return date, race_number
    return date, None

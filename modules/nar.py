from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import unicodedata
import locale

NETKEIBA_SCHEDULE_URL = "https://nar.netkeiba.com/top/schedule.html"
KEIBAGO_DIRTRACE_ROOT_URL = "https://www.keiba.go.jp/dirtgraderace"
KEIBAGO_RACELIST_URL = "https://www.keiba.go.jp/KeibaWeb/TodayRaceInfo/RaceList"
KEIBAGO_BABA_CODES = {
    "帯広": 3,
    "門別": 36,
    "盛岡": 10,
    "水沢": 11,
    "浦和": 18,
    "船橋": 19,
    "大井": 20,
    "川崎": 21,
    "金沢": 22,
    "笠松": 23,
    "名古屋": 24,
    "園田": 27,
    "姫路": 28,
    "高知": 31,
    "佐賀": 32,
}

NETKEIBA_LOCATE_IDS = {
    "門別": 30,
    "盛岡": 35,
    "水沢": 36,
    "浦和": 42,
    "船橋": 43,
    "大井": 44,
    "川崎": 45,
    "金沢": 46,
    "笠松": 47,
    "名古屋": 48,
    "園田": 50,
    "姫路": 51,
    "高知": 54,
    "佐賀": 55,
    "帯広": 65,
}

ORIGIN_TZ = ZoneInfo("Asia/Tokyo")

def get_grade_races_by_year(driver:WebDriver, year:int) -> list:
    locale.setlocale(locale.LC_TIME, 'ja_JP.UTF-8')
    now = datetime.now(ORIGIN_TZ)
    grade_races = []

    driver.get("{u}/{y}/racelist/index.html".format(
        u=KEIBAGO_DIRTRACE_ROOT_URL,
        y=year
    ))

    races = driver.find_elements(By.CSS_SELECTOR, "div#list > div.month > ul > li.js-item > a")

    for race in races:
        meta = race.find_elements(By.CSS_SELECTOR, "p")
        location = meta[1].text.split(' ')[0]
        if location in KEIBAGO_BABA_CODES.keys():
            race_data = {
                "festival_location": location,
                "race_number": None,
                "name": race.find_element(By.CSS_SELECTOR, "h4").text.replace("ステークス", "S").replace("カップ", "C"),
                "detail": race.find_element(By.CSS_SELECTOR, "h4").text,
                "grade": race.find_element(By.CSS_SELECTOR, "h4").get_attribute("class").capitalize(),
                "start_at": datetime.strptime(meta[0].text.replace("祝", ""), "%m月%d日(%a)").replace(year=year,tzinfo=ORIGIN_TZ),
                "end_at": None,
                "special_url": race.get_attribute('href').replace("racecard", "analysis"),
                "netkeiba_url": None,
                "archive_url": None,
            }
            grade_races.append(race_data)
    
    for race_data in grade_races:

        if (race_data["start_at"] - now).days < 5:
            race_data["start_at"], race_data["race_number"] = get_start_time_and_race_number(driver, race_data['detail'], race_data['start_at'], race_data['festival_location'])

        # 発走時刻が取得できた場合は5分間、それ以外は全日イベントとして定義
        if race_data["start_at"].hour != 0:
            race_data["end_at"] = race_data["start_at"] + timedelta(minutes=5)
        else:
            race_data["end_at"] = (race_data["start_at"] + timedelta(days=1)).date()
            race_data["start_at"] = race_data["start_at"].date()
        
        # レース番が取得できた場合はNETKEIBAのURLも定義
        if race_data["race_number"] != None:
            race_data["netkeiba_url"] = get_netkeiba_url(race_data["start_at"], race_data["festival_location"], race_data["race_number"], now)
        print("{d}: {name}".format(d=race_data["start_at"], name=race_data["detail"]))

        # 過去のレースの場合はアーカイブURLを追加する
        if (now - race_data["end_at"]).second > 0:
            race_data["archive_url"] = "https://www.youtube.com/@nar_keiba/search?query={n}+{y}".format(n=race_data["detail"], y=race_data["end_at"].year)
    return grade_races

def get_start_time_and_race_number(driver:WebDriver, name:str, date:datetime, location:str):

    driver.get("{u}?k_raceDate={y}%2f{m}%2f{d}&k_babaCode={b}".format(
        u=KEIBAGO_RACELIST_URL,
        b=KEIBAGO_BABA_CODES[location],
        y=date.strftime("%Y"),
        m=date.strftime("%m"),
        d=date.strftime("%d"),
    ))

    races = driver.find_elements(By.CSS_SELECTOR, "section.raceTable > table > tbody > tr.data")

    for race in races:
        race_data = race.find_elements(By.CSS_SELECTOR, "td")
        if name in unicodedata.normalize('NFKC', race_data[4].text):
            hour_str, minute_str = race_data[1].text.split(':')
            date = date.replace(hour=int(hour_str), minute=int(minute_str))
            race_number = int(race_data[0].text.replace("R", ""))
            return date, race_number
    return date, None

def get_netkeiba_url(date:datetime, location:str, race_number:int, now:datetime):
    return "https://nar.netkeiba.com/race/{p}.html?race_id={y}{l}{m:0>2}{d:0>2}{n:0>2}".format(
        p="result" if date < now else "shutuba", # 過去のレースは着順表、今後のレースは出馬表を出す
        y=date.year,
        l=NETKEIBA_LOCATE_IDS[location],
        m=date.month,
        d=date.day,
        n=race_number
    )

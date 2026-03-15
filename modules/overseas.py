import logging,re,urllib,zoneinfo
import modules.bsclient as bsc
import locale
from datetime import datetime, timedelta, date
from zoneinfo import ZoneInfo
from modules.dataclass import GradeRace, LocationName
from modules.netkeiba import get_netkeiba_url

BASE_URL="https://jra.jp"
KEIBA_URL=f"{BASE_URL}/keiba"
COMMON_URL=f"{KEIBA_URL}/common"
ORIGIN_TZ=zoneinfo.ZoneInfo("Asia/Tokyo")

def get_calendar_active_years() -> list[int]:

    years = []
    soup = bsc.get_soup(f"{KEIBA_URL}/overseas/racelist/")

    # 年が変わったばかりの時はページが去年から更新されていないことがあるので、今の最新年をページ上から取得する
    this_year_raw = soup.select_one("div#cal_block > div.race_list > div > table.main_race > caption > div.header > div.content > p").text
    if this_year_raw != None:
        this_year = int(this_year_raw.removesuffix("年 発売レース"))
        years.append(this_year)

    # それ以前の年はページ下のアーカイブ部分から取得する
    years_a = soup.select("div#backnumber_list > ul > li > a")
    for year_a in years_a:
        years.append(int(year_a.text.replace("年", "")))
    years.reverse()
    return years

def get_grade_races_by_year(year:int) -> list:

    locale.setlocale(locale.LC_TIME, 'ja_JP.UTF-8')
    overseas_races = []
    now = datetime.now(ORIGIN_TZ)

    soup = bsc.get_soup(f"https://www.jra.go.jp/keiba/overseas/racelist/{year}.html")
    if soup == None:
        logging.warning(f"failed to get {year}'s grade races")
        return []
    tr_races = soup.select("div.race_list > div > table > tbody > tr")
    for tr_race in tr_races:

        start_time_fixed = False
        race_datas = tr_race.select("td") # 0:日付, 1:国・競馬場, 2:レース名(+リンク先), 3:距離, 4:優勝馬
        race_detail = re.match(r'(.*)（(.*)）', race_datas[2].text)
        race_name = race_detail.group(1)
        race_name_short = race_name.replace("ステークス", "S").replace("カップ", "C")
        race_grade = race_detail.group(2)
        race_data = GradeRace(
            festival_location=LocationName(race_datas[1].text.strip()),
            name=race_name_short,
            detail=race_name,
            grade=race_grade,
            start_at=datetime.strptime(re.sub('（.*）', '', race_datas[0].text).strip(), "%Y年%m月%d日").replace(tzinfo=ORIGIN_TZ),
        )

        # URLがある場合の処理
        if race_datas[2].select_one("a") != None:
            race_data.special_url = BASE_URL + race_datas[2].select_one("a").get("href")

            # url構造の中に "/race/" が含まれている場合は発走時刻が公開されている（はず）
            # 発走時刻が取得できた場合は5分間、それ以外は全日イベントとして定義
            if "/race/" in race_data.special_url:
                start_time = get_start_time(race_data.special_url, year)
                if start_time != None:
                    start_time_fixed = True
                    race_data.start_at = start_time
                    race_data.end_at = start_time + timedelta(minutes=5)
        
        # URLがなく、かつ発走時刻も取れなかった場合は全日イベントとして設定
        if not start_time_fixed:
            race_data.end_at = race_data.start_at + timedelta(days=1)
            race_data.start_at = race_data.start_at.date()
            race_data.end_at = race_data.end_at.date()

        # 過去のレース、かつ2023年以降の場合はアーカイブURLを追加する
        if race_data.start_at.year >= 2023:
            if ((type(race_data.start_at) == datetime and race_data.start_at.date() < now.date())
             or (type(race_data.start_at) == date and race_data.start_at < now.date())):
                race_data.archive_url = "https://www.youtube.com/@jraofficial/search?query=" + urllib.parse.quote(race_data.name + " " + str(race_data.start_at.year))
        
        logging.info(f"### {race_data.start_at}: {race_data.detail}")
        overseas_races.append(race_data)
    return overseas_races

def get_start_time(url:str, year:int) -> datetime:

    is_pm = False
    start_time = None

    soup = bsc.get_soup(url)
    if soup == None:
        logging.warning(f"failed to get start time: {url}")
        return None
    time_datas = soup.select("div.time_area_line > div.main > div.time_area > div.unit")
    for time_data in time_datas:
        if time_data.select_one("div.cap").text == "発走予定時刻":
            time_raw = time_data.select_one("div.time > strong").text
            if "午後" in time_raw:
                is_pm = True
            time_raw = re.sub('（.*）|午前|午後', '', time_raw).strip()
            start_time = parse_jp_over24(s=time_raw, year=year, tz=ORIGIN_TZ)
            if is_pm:
                start_time += timedelta(hours=12)
    return start_time

# 25時30分などの正規化されていない時間をパースする関数
def parse_jp_over24(s: str, *, year: int | None = None, tz: ZoneInfo | None = None) -> datetime:
    PAT = re.compile(r"\s*(\d{1,2})月(\d{1,2})日(\d{1,2})時(\d{1,2})分\s*")

    m = PAT.fullmatch(s)
    if not m:
        raise ValueError("想定外の形式です: '9月13日25時30分' のように書いてください。")
    mon, day, hour, minute = map(int, m.groups())

    # 年が無いので補う（指定が無ければ現在の年）
    now = datetime.now(tz) if tz else datetime.now()
    year = year or now.year

    # 24時以降を正規化して日繰り上げ
    extra_days, hour_norm = divmod(hour, 24)

    # strptime は 0–23 時しか許さないので、正規化後の文字列で使う
    norm = f"{year:04d}-{mon:02d}-{day:02d} {hour_norm:02d}:{minute:02d}"
    dt = datetime.strptime(norm, "%Y-%m-%d %H:%M")
    dt += timedelta(days=extra_days)

    return dt.replace(tzinfo=tz) if tz else dt

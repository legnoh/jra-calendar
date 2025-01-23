import datetime,logging,requests,re,unicodedata,urllib,zoneinfo
import modules.bsclient as bsc

BASE_URL="https://jra.jp"
KEIBA_URL=f"{BASE_URL}/keiba"
COMMON_URL=f"{KEIBA_URL}/common"
ORIGIN_TZ=zoneinfo.ZoneInfo("Asia/Tokyo")

def get_calendar_active_years() -> list[str]:
    year = 2020 # 2019年以前はJRA側のテーブル形式が古いため未対応
    last_crop = False
    years = []
    while last_crop == False:
        if requests.get(f"{KEIBA_URL}/calendar{year}/active.json").status_code == 200:
            years.append(year)
            year += 1
        else:
            last_crop = True
    return years

def get_max_link_point() -> datetime:
    try:
        response = requests.get(f"{COMMON_URL}/calendar/json/setting.json")
        json = response.json()
        max_link_point = datetime.datetime.strptime(json[0]['link-point'] + " +0900", '%Y/%m/%d %z')
        return max_link_point
    except requests.exceptions.RequestException as e:
        logging.warn(f'get_max_link_point failed: {e}')
        return None

def get_grade_races_by_month(year:int, month:int, max_link_point: datetime.datetime) -> list:
    grade_races = []
    now = datetime.datetime.now(ORIGIN_TZ)

    try:
        response = requests.get(f"{COMMON_URL}/calendar/json/{year}{month:0>2}.json")
        race_raw = response.json()[0]
        race_dates = race_raw['data']

        for date in race_dates:
            race_day = int(date['date'])
            if len(date['info'][0]['gradeRace']) > 0:
                for race in date['info'][0]['gradeRace']:

                    race_data = {
                        "festival_time": None,
                        "festival_location": re.sub(r"([0-9]+)回(.*)", "\\2", date['info'][0]['race'][int(race['pos'])-1]['name']),
                        "festival_day": None,
                        "race_number": None,
                        "name": race['name'],
                        "detail": unicodedata.normalize('NFKC', race['detail']),
                        "grade": race['grade'],
                        "start_at": datetime.datetime(year, month, race_day, tzinfo=ORIGIN_TZ),
                        "end_at": None,
                        "special_url": None,
                        "netkeiba_url": None,
                        "archive_url": None,
                    }

                    if race_data['start_at'] <= max_link_point:
                        more_info = get_race_more_info(
                            race_data['detail'],
                            race_data['start_at'])
                        race_data['start_at'] = more_info['start_at']
                        race_data['special_url'] = more_info['jra_url']
                        race_data['festival_time'] = more_info['festival_time']
                        race_data['festival_day'] = more_info['festival_day']
                        race_data['race_number'] = more_info['race_number']
                        race_data['netkeiba_url'] = get_netkeiba_url(
                            race_data['start_at'],
                            race_data["festival_location"],
                            race_data["festival_time"],
                            race_data["festival_day"],
                            race_data["race_number"]
                        )
                    
                    # 過去のレースの場合はアーカイブURLを追加する
                    if race_data["start_at"].date() < now.date():
                        race_data["archive_url"] = "https://www.youtube.com/@jraofficial/search?query=" + urllib.parse.quote(race_data["name"] + " " + str(race_data["start_at"].year))

                    # 発走時刻が取得できた場合は5分間、それ以外は全日イベントとして定義
                    if race_data["start_at"].hour != 0:
                        race_data["end_at"] = race_data["start_at"] + datetime.timedelta(minutes=5)
                    else:
                        race_data["end_at"] = race_data["start_at"] + datetime.timedelta(days=1)
                        race_data["start_at"] = race_data["start_at"].date()
                        race_data["end_at"] = race_data["end_at"].date()

                    grade_races.append(race_data)
                    logging.info(f"### {race_data["start_at"]}: {race_data["detail"]}")
        return grade_races

    except requests.exceptions.RequestException:
        logging.warn('HTTP Request failed')
        return None

def get_race_more_info(name: str, date: datetime.datetime) -> dict:

    soup = bsc.get_soup(f"{KEIBA_URL}/calendar{date.year}/{date.year}/{date.month}/{date.month:0>2}{date.day:0>2}.html")
    festivals = soup.select("div#program_list > div.grid > div.cell > table")

    for festival in festivals:
        races = festival.select("tbody > tr")
        for race in races:

            # 特別競走・重賞以外は無視
            if len(race.select("td.name > p.stakes")) > 0:

                # 要素の文字列を全て結合し、スペースを消し、半角全角を揃える
                description = unicodedata.normalize('NFKC', race.select_one("td.name").text.replace(" ", "").replace("\n", ""))

                # その中にレース名が含まれていたら情報を収集
                if name in description:

                    # レース番号(1~12)
                    race_number = int(race.select_one("th.num").text.replace("レース", ""))

                    # レース発走時刻
                    race_time_raw = race.select_one("td.time").text
                    race_time_m = re.match(r"([0-9]+)時([0-9]+)分", race_time_raw)

                    # 競馬開催情報(回数と日数)
                    festival_caption = festival.select_one("caption").text.strip()
                    festival_caption_m = re.match(r"([0-9]+)回(.*)([0-9]+)日", festival_caption)
                    festival_time = int(festival_caption_m.group(1))
                    festival_day = int(festival_caption_m.group(3))

                    # 公式URL
                    jra_url = None
                    if len(race.select("td.name > p.stakes > a")) > 0:
                        jra_url = BASE_URL + race.select_one("td.name > p.stakes > a").get('href')

                    return {
                        'festival_time': festival_time,
                        'festival_day': festival_day,
                        'race_number': race_number,
                        'start_at': datetime.datetime(
                            year=date.year,
                            month=date.month,
                            day=date.day,
                            hour=int(race_time_m.group(1)),
                            minute=int(race_time_m.group(2)),
                            tzinfo=ORIGIN_TZ,
                        ),
                        'jra_url': jra_url,
                    }
    logging.error(f"no festival data found: {name} / {date}")
    return {}

def get_netkeiba_url(date: datetime.datetime, location: str, time:int, day:int, race_number: int) -> str:

    # 過去のレースは着順表、今後のレースは出馬表を出す
    now = datetime.datetime.now(tz=ORIGIN_TZ)
    path = "result" if date < now else "shutuba"

    # 競馬場名はIDに変換する
    locations = ["札幌", "函館", "福島", "新潟", "東京", "中山", "中京", "京都", "阪神", "小倉"]

    return "https://race.netkeiba.com/race/{p}.html?race_id={y}{l:0>2}{t:0>2}{d:0>2}{n:0>2}".format(
        p=path, y=date.year, l=locations.index(location)+1, t=time, d=day, n=race_number
    )

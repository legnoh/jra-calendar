from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
import datetime,logging,requests,re,zoneinfo

BASE_URL="https://jra.jp/keiba"
COMMON_URL="{u}/common".format(u=BASE_URL)
ORIGIN_TZ=zoneinfo.ZoneInfo("Asia/Tokyo")

def get_calendar_active_years(driver) -> list:
    driver.get("{u}/calendar/".format(u=BASE_URL))
    years_li = driver.find_elements(By.CSS_SELECTOR, "div#mainBody > div.cal_year > ul > li")
    years = []
    for year_li in years_li:
        years.append(int(year_li.text))
    years.sort()
    return years

def get_max_link_point() -> datetime:
    try:
        response = requests.get(
            url="{u}/calendar/json/setting.json".format(u=COMMON_URL),
        )
        json = response.json()
        max_link_point = datetime.datetime.strptime(json[0]['link-point'] + " +0900", '%Y/%m/%d %z')
        return max_link_point
    except requests.exceptions.RequestException:
        logging.warn('HTTP Request failed')
        return None

def get_grade_races_by_month(driver:WebDriver, year:int, month:int, max_link_point: datetime.datetime) -> list:
    grade_races = []
    now = datetime.datetime.now(ORIGIN_TZ)

    try:
        response = requests.get(
            url="{u}/calendar/json/{y}{m:0>2}.json".format(u=COMMON_URL, y=year, m=month),
        )
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
                        "detail": race['detail'],
                        "grade": race['grade'],
                        "start_at": datetime.datetime(year=year, month=month, day=race_day, tzinfo=ORIGIN_TZ),
                        "end_at": None,
                        "special_url": None,
                        "netkeiba_url": None,
                        "archive_url": None,
                    }

                    if race_data['start_at'] <= max_link_point:
                        more_info = get_race_more_info(
                            driver,
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
                        race_data["archive_url"] = "https://www.youtube.com/@nar_keiba/search?query={n}+{y}".format(n=race_data["name"], y=race_data["start_at"].year)

                    # 発走時刻が取得できた場合は5分間、それ以外は全日イベントとして定義
                    if race_data["start_at"].hour != 0:
                        race_data["end_at"] = race_data["start_at"] + datetime.timedelta(minutes=5)
                    else:
                        race_data["end_at"] = race_data["start_at"] + datetime.timedelta(days=1)
                        race_data["start_at"] = race_data["start_at"].date()
                        race_data["end_at"] = race_data["end_at"].date()

                    grade_races.append(race_data)
                    print("{d}: {name}".format(d=race_data["start_at"], name=race_data["detail"]))
        return grade_races

    except requests.exceptions.RequestException:
        logging.warn('HTTP Request failed')
        return None

def get_race_more_info(driver:WebDriver, name: str, date: datetime.datetime) -> dict:

    driver.get("{u}/calendar{y}/{y}/{m}/{m:0>2}{d:0>2}.html".format(u=BASE_URL, y=date.year,m=date.month,d=date.day))
    festivals = driver.find_elements(By.CSS_SELECTOR, "div#program_list > div.grid > div.cell > table")

    driver.implicitly_wait(0.1)

    for festival in festivals:
        races = festival.find_elements(By.CSS_SELECTOR, "tbody > tr")
        for race in races:

            # 特別競走・重賞以外は無視
            if len(race.find_elements(By.CSS_SELECTOR,"td.name > p.stakes")) > 0:

                # 要素の文字列を全て結合
                description = race.find_element(By.CSS_SELECTOR,"td.name").text.replace("\n", "")

                # その中にレース名が含まれていたら情報を収集
                if name in description :

                    # レース番号(1~12)
                    race_number = int(race.find_element(By.CSS_SELECTOR, "th.num").text.replace("レース", ""))

                    # レース発走時刻
                    race_time_raw = race.find_element(By.CSS_SELECTOR, "td.time").text
                    race_time_m = re.match(r"([0-9]+)時([0-9]+)分", race_time_raw)

                    # 競馬開催情報(回数と日数)
                    festival_caption = festival.find_element(By.CSS_SELECTOR, "caption").text
                    festival_caption_m = re.match(r"([0-9]+)回(.*)([0-9]+)日", festival_caption)
                    festival_time = int(festival_caption_m.group(1))
                    festival_day = int(festival_caption_m.group(3))

                    # 公式URL
                    jra_url = None
                    if len(race.find_elements(By.CSS_SELECTOR,"td.name > p.stakes > a")) > 0:
                        jra_url = race.find_element(By.CSS_SELECTOR,"td.name > p.stakes > a").get_attribute('href')
                    
                    driver.implicitly_wait(10)

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
    driver.implicitly_wait(10)
    return date

def get_netkeiba_url(date: datetime.datetime, location: str, time:int, day:int, race_number: int) -> str:

    # 過去のレースは着順表、今後のレースは出馬表を出す
    now = datetime.datetime.now(tz=ORIGIN_TZ)
    path = "result" if date < now else "shutuba"

    # 競馬場名はIDに変換する
    locations = ["札幌", "函館", "福島", "新潟", "東京", "中山", "中京", "京都", "阪神", "小倉"]

    return "https://race.netkeiba.com/race/{p}.html?race_id={y}{l:0>2}{t:0>2}{d:0>2}{n:0>2}".format(
        p=path, y=date.year, l=locations.index(location)+1, t=time, d=day, n=race_number
    )

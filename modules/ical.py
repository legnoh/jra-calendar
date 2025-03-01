from icalendar import Event
import base64,datetime,zoneinfo

BASE_URL="https://jra.jp/keiba"
COMMON_URL=f"{BASE_URL}/common"
ORIGIN_TZ=zoneinfo.ZoneInfo("Asia/Tokyo")

# 各競馬場のgeoの位置は徒歩で行った際の合理的な入場門の位置にする
# (競馬場の中心にピンが立っていると使えない経路が出てくることが多々あるため)
LOCATIONS_INFO={
    "札幌": {
        "name": "札幌競馬場",
        "address": "〒060-0016, 北海道札幌市中央区, 北16条西16-1-1",
        "geo": "43.076045,141.323257",
        "admission": "https://jra-tickets.jp/",
        "reservation": "https://jra-tickets.jp/",
        "betting": "https://www.ipat.jra.go.jp/",
        "live": None,
    },
    "函館": {
        "name": "函館競馬場",
        "address": "〒042-8585, 北海道函館市, 駒場町12-2",
        "geo": "41.783556,140.775696",
        "admission": "https://jra-tickets.jp/",
        "reservation": "https://jra-tickets.jp/",
        "betting": "https://www.ipat.jra.go.jp/",
        "live": None,
    },
    "福島": {
        "name": "福島競馬場",
        "address": "〒960-8114, 福島県福島市, 松浪町9-23",
        "geo": "37.764036,140.479352",
        "admission": "https://jra-tickets.jp/",
        "reservation": "https://jra-tickets.jp/",
        "betting": "https://www.ipat.jra.go.jp/",
        "live": None,
    },
    "新潟": {
        "name": "新潟競馬場",
        "address": "〒950-3301, 新潟県新潟市北区, 笹山3490",
        "geo": "37.948938,139.183418",
        "admission": "https://jra-tickets.jp/",
        "reservation": "https://jra-tickets.jp/",
        "betting": "https://www.ipat.jra.go.jp/",
        "live": None,
    },
    "東京": {
        "name": "東京競馬場",
        "address": "〒183-0024, 東京都府中市, 日吉町1-1",
        "geo": "35.664474,139.480346",
        "admission": "https://jra-tickets.jp/",
        "reservation": "https://jra-tickets.jp/",
        "betting": "https://www.ipat.jra.go.jp/",
        "live": None,
    },
    "中山": {
        "name": "中山競馬場",
        "address": "〒273-0037, 千葉県船橋市, 古作1-1-1",
        "geo": "35.727043,139.959520",
        "admission": "https://jra-tickets.jp/",
        "reservation": "https://jra-tickets.jp/",
        "betting": "https://www.ipat.jra.go.jp/",
        "live": None,
    },
    "中京": {
        "name": "中京競馬場",
        "address": "〒470-1132, 愛知県豊明市間米町, 敷田1225",
        "geo": "35.065468,136.987098",
        "admission": "https://jra-tickets.jp/",
        "reservation": "https://jra-tickets.jp/",
        "betting": "https://www.ipat.jra.go.jp/",
        "live": None,
    },
    "京都": {
        "name": "京都競馬場",
        "address": "〒612-8265, 京都府京都市伏見区, 葭島渡場島町32",
        "geo": "34.907831,135.724072",
        "admission": "https://jra-tickets.jp/",
        "reservation": "https://jra-tickets.jp/",
        "betting": "https://www.ipat.jra.go.jp/",
        "live": None,
    },
    "阪神": {
        "name": "阪神競馬場",
        "address": "〒665-0053, 兵庫県宝塚市, 駒の町1-1",
        "geo": "34.777831,135.360592",
        "admission": "https://jra-tickets.jp/",
        "reservation": "https://jra-tickets.jp/",
        "betting": "https://www.ipat.jra.go.jp/",
        "live": None,
    },
    "小倉": {
        "name": "小倉競馬場",
        "address": "〒802-0841, 福岡県北九州市小倉南区, 北方4-5-1",
        "geo": "33.843143,130.876244",
        "admission": "https://jra-tickets.jp/",
        "reservation": "https://jra-tickets.jp/",
        "betting": "https://www.ipat.jra.go.jp/",
        "live": None,
    },
    "帯広": {
        "name": "帯広競馬場",
        "address": "〒080-0023, 北海道帯広市西13条, 南9-1",
        "geo": "42.921079,143.183481",
        "admission": "https://banei-keiba.or.jp/access.php",
        "reservation": "https://banei-keiba.or.jp/spot_premiumlounge.php",
        "betting": None,
        "live": "https://www.youtube.com/@user-di2dh2dc4q/streams",
    },
    "門別": {
        "name": "門別競馬場",
        "address": "〒055-0008, 北海道沙流郡日高町, 富川駒丘76-1",
        "geo": "42.538360,141.997367",
        "admission": "http://www.hokkaidokeiba.net/guide/access/fbus.php",
        "reservation": None,
        "betting": "https://n.ipat.jra.go.jp",
        "live": "https://www.youtube.com/@live2820/streams",
    },
    "盛岡": {
        "name": "盛岡競馬場",
        "address": "〒020-0803, 岩手県盛岡市新庄, 上八木田10-10-4",
        "geo": "39.696113,141.221176",
        "admission": "https://www.iwatekeiba.or.jp/race/free_bus",
        "reservation": "https://www.google.com/search?q=site:www.iwatekeiba.or.jp/news+指定席",
        ""
        "betting": "https://n.ipat.jra.go.jp",
        "live": "https://www.youtube.com/@IwateKeibaITV/streams",
    },
    "水沢": {
        "name": "水沢競馬場",
        "address": "〒023-0831, 岩手県奥州市水沢姉体町, 阿久戸1-2",
        "geo": "39.130318,141.166911",
        "admission": "https://www.iwatekeiba.or.jp/race/free_bus",
        "reservation": None,
        "betting": "https://n.ipat.jra.go.jp",
        "live": "https://www.youtube.com/@IwateKeibaITV/streams",
    },
    "浦和": {
        "name": "浦和競馬場",
        "address": "〒336-0016, 埼玉県さいたま市南区, 大谷場1-8-42",
        "geo": "35.855503,139.669410",
        "admission": "https://www.urawa-keiba.jp/navi/facility03.html#number02",
        "reservation": "https://www.google.com/search?q=site:keiba.rakuten.co.jp+%22浦和競馬%22+%22入場%22",
        "betting": "https://n.ipat.jra.go.jp",
        "live": "https://www.youtube.com/@user-vh3fg5mt1c/streams",
    },
    "船橋": {
        "name": "船橋競馬場",
        "address": "〒273-0013, 千葉県船橋市, 若松1-2-1",
        "geo": "35.688094,139.994934",
        "admission": "https://www.f-keiba.com/guide/",
        "reservation": "https://www.google.com/search?q=site:blog.f-keiba.com+%22入場%22",
        "betting": "https://n.ipat.jra.go.jp",
        "live": "https://www.youtube.com/@funabashi-keiba/streams",
    },
    "大井": {
        "name": "大井競馬場",
        "address": "〒140-0012, 東京都品川区, 勝島2-1-2",
        "geo": "35.595758,139.744662",
        "admission": "https://www.tokyocitykeiba.com/guide/about_tck/",
        "reservation": "https://www.tokyocitykeiba.com/reservedseat/buying_guide/",
        "betting": "https://n.ipat.jra.go.jp",
        "live": "https://www.youtube.com/@tckkeiba/streams",

    },
    "川崎": {
        "name": "川崎競馬場",
        "address": "〒210-0011, 神奈川県川崎市川崎区, 富士見1-5-1",
        "geo": "35.534072,139.710847",
        "admission": "https://www.kawasaki-keiba.jp/info/business_day/",
        "reservation": "https://www.kawasaki-keiba.jp/seat/reserved/",
        "betting": "https://n.ipat.jra.go.jp",
        "live": "https://www.youtube.com/@user-se7me6tw7q/streams",
    },
    "金沢": {
        "name": "金沢競馬場",
        "address": "〒920-3105, 石川県金沢市八田町, 西1 金沢競馬場",
        "geo": "36.634042,136.673253",
        "admission": "https://www.kanazawakeiba.com/facilities/outline/",
        "reservation": "https://www.google.com/search?q=site:www.kanazawakeiba.com+指定席",
        "betting": "https://n.ipat.jra.go.jp",
        "live": "https://www.youtube.com/@user-dx7rm6oz6r/streams",
    },
    "笠松": {
        "name": "笠松競馬場",
        "address": "〒501-6036, 岐阜県羽島郡笠松町, 若葉町12",
        "geo": "35.372466,136.765175",
        "admission": "https://www.kasamatsu-keiba.com/facilities",
        "reservation": "https://www.google.com/search?q=site:www.kasamatsu-keiba.com+有料席",
        "betting": "https://n.ipat.jra.go.jp",
        "live": "https://www.youtube.com/@user-lm8ln1kk9j/streams",
    },
    "名古屋": {
        "name": "名古屋競馬場",
        "address": "〒498-0065, 愛知県弥富市, 駒野町1",
        "geo": "35.055350,136.785048",
        "admission": "https://www.nagoyakeiba.com/guide/information.html",
        "reservation": "https://www.nagoyakeiba.com/reservation/index.html",
        "betting": "https://n.ipat.jra.go.jp",
        "live": "https://www.youtube.com/@user-sx4xe4bs5r/streams",
    },
    "園田": {
        "name": "園田競馬場",
        "address": "〒661-0951, 兵庫県尼崎市, 田能2-1-1",
        "geo": "34.764694,135.445509",
        "admission": "https://www.sonoda-himeji.jp/guide/sbet",
        "reservation": "https://www.google.com/search?q=site:www.sonoda-himeji.jp+園田競馬場+指定席",
        "betting": "https://n.ipat.jra.go.jp",
        "live": "https://www.youtube.com/@sonodahimejiweb/streams",
    },
    "姫路": {
        "name": "姫路競馬場",
        "address": "〒670-0882, 兵庫県姫路市, 広峰2-7-80",
        "geo": "34.855566,134.704458",
        "admission": "https://www.sonoda-himeji.jp/guide/hbet",
        "reservation": "https://www.google.com/search?q=site:www.sonoda-himeji.jp+姫路競馬場+指定席",
        "betting": "https://n.ipat.jra.go.jp",
        "live": "https://www.youtube.com/@sonodahimejiweb/streams",
    },
    "高知": {
        "name": "高知競馬場",
        "address": "〒781-0271, 高知県高知市長浜, 宮田2000",
        "geo": "33.504549,133.528300",
        "admission": "https://www.keiba.or.jp/?cat=74",
        "reservation": "https://www.google.com/search?q=site:www.keiba.or.jp+特別観覧席",
        "betting": "https://n.ipat.jra.go.jp",
        "live": "https://www.youtube.com/@KeibaOrJp/streams",
    },
    "佐賀": {
        "name": "佐賀競馬場",
        "address": "〒841-0073, 佐賀県鳥栖市, 江島町字西谷3256-228",
        "geo": "33.350995,130.469143",
        "admission": "https://www.sagakeiba.net/guide/#map02",
        "reservation": "https://www.sagakeiba.net/guide/?id=tab2",
        "betting": "https://n.ipat.jra.go.jp",
        "live": "https://www.youtube.com/@sagakeibaofficial/streams",
    },
    "シャティン": {
        "name": "Sha Tin Racecourse",
        "address": "Sha Tin, New Territories, Hong Kong SAR, China",
        "geo": "22.400634, 114.204179",
        "admission": None,
        "reservation": None,
        "betting": "https://www.ipat.jra.go.jp/",
        "live": "https://sp.gch.jp/",
        "flag": "🇭🇰",
    },
    "パリロンシャン": {
        "name": "Longchamp Racecourse",
        "address": "2 Route des Tribunes, 75016 Paris, France",
        "geo": "48.860889, 2.231523",
        "admission": None,
        "reservation": None,
        "betting": "https://www.ipat.jra.go.jp/",
        "live": "https://sp.gch.jp/",
        "flag": "🇫🇷",
    },
    "ドーヴィル": {
        "name": "Deauville-La Touques Racecourse",
        "address": "45 Avenue Hocquart de Turtot, 14800 Deauville, France",
        "geo": "49.353256, 0.073450",
        "admission": None,
        "reservation": None,
        "betting": "https://www.ipat.jra.go.jp/",
        "live": "https://sp.gch.jp/",
        "flag": "🇫🇷",
    },
    "シャンティイ": {
        "name": "Chantilly Racecourse",
        "address": "Route des Aigles & Avenue de la Plaine des Aigles, 60500 Chantilly, France",
        "geo": "49.190400, 2.474290",
        "admission": None,
        "reservation": None,
        "betting": "https://www.ipat.jra.go.jp/",
        "live": "https://sp.gch.jp/",
        "flag": "🇫🇷",
    },
    "メイダン": {
        "name": "Meydan Racecourse",
        "address": "Al Meydan St 10, Dubai, United Arab Emirates",
        "geo": "25.156783, 55.304833",
        "admission": None,
        "reservation": None,
        "betting": "https://www.ipat.jra.go.jp/",
        "live": "https://sp.gch.jp/",
        "flag": "🇯🇴",
    },
    "デルマー": {
        "name": "Del Mar Racetrack",
        "address": "2260 Jimmy Durante Blvd, Del Mar, CA 92014, United States",
        "geo": "32.976304, -117.262959",
        "admission": None,
        "reservation": None,
        "betting": "https://www.ipat.jra.go.jp/",
        "live": "https://sp.gch.jp/",
        "flag": "🇺🇸",
    },
    "チャーチルダウンズ": {
        "name": "Churchill Downs",
        "address": "700 Central Ave, Louisville, KY 40208, United States",
        "geo": "38.202711, -85.770221",
        "admission": None,
        "reservation": None,
        "betting": "https://www.ipat.jra.go.jp/",
        "live": "https://sp.gch.jp/",
        "flag": "🇺🇸",
    },
    "ピムリコ": {
        "name": "Pimlico Race Course",
        "address": "5201 Park Heights Ave, Baltimore, MD 21215, United States",
        "geo": "39.353331, -76.673026",
        "admission": None,
        "reservation": None,
        "betting": "https://www.ipat.jra.go.jp/",
        "live": "https://sp.gch.jp/",
        "flag": "🇺🇸",
    },
    "サラトガ": {
        "name": "Saratoga Race Course",
        "address": "267 Union Ave, Saratoga Springs, NY 12866, United States",
        "geo": "43.073465, -73.769782",
        "admission": None,
        "reservation": None,
        "betting": "https://www.ipat.jra.go.jp/",
        "live": "https://sp.gch.jp/",
        "flag": "🇺🇸",
    },
    "サンタアニタパーク": {
        "name": "Santa Anita Park Racetrack",
        "address": "285 W Huntington Dr, Arcadia, CA 91007, United States",
        "geo": "34.138920, -118.045285",
        "admission": None,
        "reservation": None,
        "betting": "https://www.ipat.jra.go.jp/",
        "live": "https://sp.gch.jp/",
        "flag": "🇺🇸",
    },
    "ベルモントパーク": {
        "name": "Belmont Park",
        "address": "2150 Hempstead Turnpike, Elmont, NY 11003, United States",
        "geo": "40.714956, -73.722065",
        "admission": None,
        "reservation": None,
        "betting": "https://www.ipat.jra.go.jp/",
        "live": "https://sp.gch.jp/",
        "flag": "🇺🇸",
    },
    "ランドウィック": {
        "name": "Royal Randwick Racecourse",
        "address": "Ascot St, Randwick NSW 2031, Australia",
        "geo": "-33.910455, 151.230231",
        "admission": None,
        "reservation": None,
        "betting": "https://www.ipat.jra.go.jp/",
        "live": "https://sp.gch.jp/",
        "flag": "🇦🇺",
    },
    "ムーニーバレー": {
        "name": "Moonee Valley Racing Club",
        "address": "Feehan Ave, Moonee Ponds VIC 3039, Australia",
        "geo": "-37.763436, 144.930463",
        "admission": None,
        "reservation": None,
        "betting": "https://www.ipat.jra.go.jp/",
        "live": "https://sp.gch.jp/",
        "flag": "🇦🇺",
    },
    "フレミントン": {
        "name": "Flemington Racecourse",
        "address": "448 Epsom Rd, Flemington VIC 3031, Australia",
        "geo": "-37.788539, 144.911756",
        "admission": None,
        "reservation": None,
        "betting": "https://www.ipat.jra.go.jp/",
        "live": "https://sp.gch.jp/",
        "flag": "🇦🇺",
    },
    "コーフィールド": {
        "name": "Caulfield Racecourse",
        "address": "Station Street, Caulfield East VIC 3145, Australia",
        "geo": "-37.881634, 145.039505",
        "admission": None,
        "reservation": None,
        "betting": "https://www.ipat.jra.go.jp/",
        "live": "https://sp.gch.jp/",
        "flag": "🇦🇺",
    },
    "アスコット": {
        "name": "Ascot Racecourse",
        "address": "High Street, Ascot, SL5 7JX, England",
        "geo": "51.412203, -0.679350",
        "admission": None,
        "reservation": None,
        "betting": "https://www.ipat.jra.go.jp/",
        "live": "https://sp.gch.jp/",
        "flag": "🇬🇧",
    },
    "ヨーク": {
        "name": "York Racecourse",
        "address": "Knavesmire Road, York, YO23 1EX, England",
        "geo": "53.940591, -1.092324",
        "admission": None,
        "reservation": None,
        "betting": "https://www.ipat.jra.go.jp/",
        "live": "https://sp.gch.jp/",
        "flag": "🇬🇧",
    },
    "サンダウン": {
        "name": "Sandown Park Racecourse",
        "address": "Portsmouth Road, Esher, KT10 9AJ, England",
        "geo": "51.373665, -0.362820",
        "admission": None,
        "reservation": None,
        "betting": "https://www.ipat.jra.go.jp/",
        "live": "https://sp.gch.jp/",
        "flag": "🇬🇧",
    },
    "グッドウッド": {
        "name": "Goodwood Racecourse",
        "address": "Chichester, PO18 0PS, England",
        "geo": "50.891997, -0.744264",
        "admission": None,
        "reservation": None,
        "betting": "https://www.ipat.jra.go.jp/",
        "live": "https://sp.gch.jp/",
        "flag": "🇬🇧",
    },
    "エプソムダウンズ": {
        "name": "Epsom Downs Racecourse",
        "address": "Surrey, KT18 5LQ, England",
        "geo": "51.313338, -0.255605",
        "admission": None,
        "reservation": None,
        "betting": "https://www.ipat.jra.go.jp/",
        "live": "https://sp.gch.jp/",
        "flag": "🇬🇧",
    },
    "レパーズタウン": {
        "name": "Leopardstown Racecourse",
        "address": "Leopardstown Pavilion, Leopardstown Racecourse, Dublin 18, D18 Y9T1, Ireland",
        "geo": "53.266490, -6.193322",
        "admission": None,
        "reservation": None,
        "betting": "https://www.ipat.jra.go.jp/",
        "live": "https://sp.gch.jp/",
        "flag": "🇮🇪",
    },
    "キングアブドゥルアジーズ": {
        "name": "King Abdulaziz Equestrian Field",
        "address": "13638, Rumah, Saudi Arabia",
        "geo": "24.986442, 46.786329",
        "admission": None,
        "reservation": None,
        "betting": "https://www.ipat.jra.go.jp/",
        "live": "https://sp.gch.jp/",
        "flag": "🇸🇦",
    },
    "アルライヤン": {
        "name": "Qatar Racing and Equestrian Club",
        "address": "Building Number 104, Al Qalah Street, Zone 53, Al Rayyan, Qatar",
        "geo": "25.282974, 51.430688",
        "admission": None,
        "reservation": None,
        "betting": None,
        "live": "https://sp.gch.jp/",
        "flag": "🇶🇦",
    },
}

def get_x_apple_structured_location(race_course: str):
    infoset = LOCATIONS_INFO[race_course]
    return {
        'name': "X-APPLE-STRUCTURED-LOCATION",
        'value': f"geo:{infoset['geo']}",
        'parameters': {
            "VALUE": "URI",
            'X-APPLE-REFERENCEFRAME': "1",
            'X-TITLE': infoset['name'],
            'X-ADDRESS': infoset['address'],
        }
    }

def create_event_block(race: dict):

    now = datetime.datetime.now(tz=ORIGIN_TZ)

    # UIDを作る
    raw_uid = f"{race['start_at']}{race['name']}"
    uid_enc = raw_uid.encode('utf-8')
    uid = base64.b64encode(uid_enc)

    # タイトルを作る（グレード表記の部分は絵文字に書き換える）
    summary = f"{race['grade'].replace("J・","").replace("G1","🥇").replace("G2","🥈").replace("G3","🥉").replace("Jpn1","🥇").replace("Jpn2","🥈").replace("Jpn3","🥉")}{race['name']}"

    # 競馬場の情報を取得する(X-APPLE-STRUCTURED_LOCATIONの形式に合わせる)
    x_apple_structured_location = get_x_apple_structured_location(race["festival_location"])

    # 本文を作る
    urls = []
    locateinfo = LOCATIONS_INFO[race["festival_location"]]

    if "flag" in locateinfo:
        summary = locateinfo["flag"] + summary
    if race["special_url"] != None:
        urls.append(f"分析: {race["special_url"]}")
    if race["netkeiba_url"] != None:
        if type(race["end_at"]) is datetime.date:
            urls.append(f"出走: {race["netkeiba_url"]}")
        elif type(race["end_at"]) is datetime.datetime:
            if now < race["end_at"]:
                urls.append(f"出走: {race["netkeiba_url"]}")
            else:
                urls.append(f"結果: {race["netkeiba_url"]}")
    if race["archive_url"] != None:
        urls.append(f"映像: {race["archive_url"]}")
    if locateinfo["admission"] != None:
        urls.append(f"入場: {locateinfo["admission"]}")
    if locateinfo["reservation"] != None:
        urls.append(f"予約: {locateinfo["reservation"]}")
    if locateinfo["betting"] != None:
        urls.append(f"投票: {locateinfo["betting"]}")
    if locateinfo["live"] != None:
        urls.append(f"LIVE: {locateinfo["live"]}")
    description = "\n".join(urls)

    event = Event()
    event.add('UID', uid)
    event.add('SUMMARY', summary)
    event.add('DESCRIPTION', description)
    event.add('DTSTART', race["start_at"])
    event.add('DTEND', race["end_at"])
    event.add('LOCATION', f"{x_apple_structured_location['parameters']['X-TITLE']}\n{x_apple_structured_location['parameters']['X-ADDRESS']}"),
    event.add(**x_apple_structured_location)
    event.add('TRANSP', 'TRANSPARENT')
    if race['netkeiba_url'] != None:
        event.add('URL', race['netkeiba_url'], parameters={'VALUE': 'URI'})
    return event

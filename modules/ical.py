from icalendar import Event
import base64

BASE_URL="https://jra.jp/keiba"
COMMON_URL="{u}/common".format(u=BASE_URL)
NYUJO_URL="https://jra-pass.pia.jp/"

LOCATIONS_SHORTNAME=["札幌", "函館", "福島", "新潟", "東京", "中山", "中京", "京都", "阪神", "小倉"]
LOCATIONS_INFO=[
    {
        "name": "札幌競馬場",
        "address": "〒060-0016, 北海道札幌市中央区, 北16条西16-1-1",
        "geo": "43.076482,141.327020",
    },
    {
        "name": "函館競馬場",
        "address": "〒042-8585, 北海道函館市, 駒場町12-2",
        "geo": "41.782873,140.775513",
    },
    {
        "name": "福島競馬場",
        "address": "〒960-8114, 福島県福島市, 松浪町9-23",
        "geo": "37.764676,140.482500",
    },
    {
        "name": "新潟競馬場",
        "address": "〒950-3301, 新潟県新潟市北区, 笹山3490",
        "geo": "37.947226,139.186757",
    },
    {
        "name": "東京競馬場",
        "address": "〒183-0024, 東京都府中市, 日吉町1-1",
        "geo": "35.662527,139.485726",
    },
    {
        "name": "中山競馬場",
        "address": "〒273-0037, 千葉県船橋市, 古作1丁目1-1",
        "geo": "35.727043,139.959520",
    },
    {
        "name": "中京競馬場",
        "address": "〒470-1132, 愛知県豊明市, 間米町敷田1225",
        "geo": "35.066040,136.992776",
    },
    {
        "name": "京都競馬場",
        "address": "〒612-8265, 京都府京都市伏見区, 葭島渡場島町32",
        "geo": "34.906373,135.726514",
    },
    {
        "name": "阪神競馬場",
        "address": "〒665-0053, 兵庫県宝塚市, 駒の町1-1",
        "geo": "34.780536,135.363665",
    },
    {
        "name": "小倉競馬場",
        "address": "〒802-0841, 福岡県北九州市小倉南区, 北方4-5-1",
        "geo": "33.842707,130.872531",
    },
]

def get_x_apple_structured_location(race_course: str):
    infoset = LOCATIONS_INFO[LOCATIONS_SHORTNAME.index(race_course)]
    return {
        'name': "X-APPLE-STRUCTURED-LOCATION",
        'value': "geo:{g}".format(g=infoset['geo']),
        'parameters': {
            "VALUE": "URI",
            "X-APPLE-REFERENCEFRAME": "1",
            'X-TITLE': "{n}".format(n=infoset['name'],a=infoset['address'])
        }
    }

def create_event_block(race: dict):

    # UIDを作る
    raw_uid = "{s}{t}".format(s=race['start_at'],t=race['name'])
    uid_enc = raw_uid.encode('utf-8')
    uid = base64.b64encode(uid_enc)

    # タイトルを作る（G1/G2/G3の部分はローマ数字に書き換える）
    summary = "{n}({g})".format(
        n=race['name'],
        g=race['grade'].replace("1","Ⅰ").replace("2","Ⅱ").replace("3","Ⅲ")
    )

    # 競馬場の情報を取得する(X-APPLE-STRUCTURED_LOCATIONの形式に合わせる)
    x_apple_structured_location = get_x_apple_structured_location(race["festival_location"])

    # 本文を作る
    description = '特集ページ: {url}\n入場: {nurl}'.format(url=race["jra_url"],nurl=NYUJO_URL)

    event = Event()
    event.add('UID', uid)
    event.add('SUMMARY', summary)
    event.add('DESCRIPTION', description)
    event.add('DTSTART', race["start_at"])
    event.add('DTEND', race["end_at"])
    event.add('LOCATION', x_apple_structured_location['parameters']['X-TITLE'])
    event.add(**x_apple_structured_location)
    event.add('TRANSP', 'TRANSPARENT')
    event.add('URL', race['netkeiba_url'], parameters={'VALUE': 'URI'})
    return event

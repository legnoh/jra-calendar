from dataclasses import dataclass
from datetime import date, datetime
from enum import Enum
from zoneinfo import ZoneInfo
from typing import Optional, Union


class KeibaType(Enum):
    JRA = "jra"
    NAR = "nar"
    OVERSEAS = "overseas"


class LocationName(Enum):
    SAPPORO = "札幌"
    HAKODATE = "函館"
    FUKUSHIMA = "福島"
    NIIGATA = "新潟"
    TOKYO = "東京"
    NAKAYAMA = "中山"
    CHUKYO = "中京"
    KYOTO = "京都"
    HANSHIN = "阪神"
    KOKURA = "小倉"
    OBIHIRO = "帯広"
    MONBETSU = "門別"
    MORIOKA = "盛岡"
    MIZUSAWA = "水沢"
    URAWA = "浦和"
    FUNABASHI = "船橋"
    OI = "大井"
    KAWASAKI = "川崎"
    KANAZAWA = "金沢"
    KASAMATSU = "笠松"
    NAGOYA = "名古屋"
    SONODA = "園田"
    HIMEJI = "姫路"
    KOCHI = "高知"
    SAGA = "佐賀"
    SHA_TIN = "シャティン"
    PARIS_LONGCHAMP = "パリロンシャン"
    DEAUVILLE = "ドーヴィル"
    CHANTILLY = "シャンティイ"
    MEYDAN = "メイダン"
    DEL_MAR = "デルマー"
    CHURCHILL_DOWNS = "チャーチルダウンズ"
    PIMLICO = "ピムリコ"
    SARATOGA = "サラトガ"
    SANTA_ANITA_PARK = "サンタアニタパーク"
    BELMONT_PARK = "ベルモントパーク"
    RANDWICK = "ランドウィック"
    MOONEE_VALLEY = "ムーニーバレー"
    FLEMINGTON = "フレミントン"
    CAULFIELD = "コーフィールド"
    ASCOT = "アスコット"
    YORK = "ヨーク"
    SANDOWN = "サンダウン"
    GOODWOOD = "グッドウッド"
    EPSOM_DOWNS = "エプソムダウンズ"
    LEOPARDSTOWN = "レパーズタウン"
    KING_ABDULAZIZ = "キングアブドゥルアジーズ"
    AL_RAYYAN = "アルライヤン"


@dataclass
class LocationInfo:
    name: str
    address: str
    geo: str
    admission: Optional[str] = None
    reservation: Optional[str] = None
    betting: Optional[str] = None
    live: Optional[str] = None
    youtube_channel_id: Optional[str] = None
    flag: Optional[str] = None
    keiba_type: Optional[KeibaType] = None
    netkeiba_id: Optional[Union[int, str]] = None
    keibago_babacode: Optional[int] = None
    timezone: Optional[ZoneInfo] = None


@dataclass
class GradeRace:
    festival_location: LocationName
    name: str
    detail: str
    grade: str
    start_at: Union[datetime, date]
    end_at: Optional[Union[datetime, date]] = None
    festival_time: Optional[int] = None
    festival_day: Optional[int] = None
    race_number: Optional[int] = None
    special_url: Optional[str] = None
    netkeiba_url: Optional[str] = None
    live_url: Optional[str] = None
    archive_url: Optional[str] = None

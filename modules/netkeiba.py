import datetime,zoneinfo
from typing import Optional
from modules.locations import LOCATIONS_INFO
from modules.dataclass import KeibaType, LocationName

ORIGIN_TZ = zoneinfo.ZoneInfo("Asia/Tokyo")


def get_netkeiba_url(
    date: datetime.datetime,
    location: LocationName,
    race_number: int,
    festival_time: Optional[int] = None,
    festival_day: Optional[int] = None,
) -> str:
    now = datetime.datetime.now(tz=ORIGIN_TZ)
    path = "result" if date < now else "shutuba"
    loc = LOCATIONS_INFO[location]

    if loc.keiba_type == KeibaType.JRA:
        return "https://race.netkeiba.com/race/{p}.html?race_id={y}{l:0>2}{t:0>2}{d:0>2}{n:0>2}".format(
            p=path, y=date.year, l=loc.netkeiba_id, t=festival_time, d=festival_day, n=race_number
        )
    elif loc.keiba_type == KeibaType.NAR:
        return "https://nar.netkeiba.com/race/{p}.html?race_id={y}{l}{m:0>2}{d:0>2}{n:0>2}".format(
            p=path, y=date.year, l=loc.netkeiba_id, m=date.month, d=date.day, n=race_number
        )
    elif loc.keiba_type == KeibaType.OVERSEAS:
        local_dt = date.astimezone(loc.timezone)
        return "https://race.netkeiba.com/race/{p}.html?race_id={y}{l}{m:0>2}{d:0>2}{n:0>2}".format(
            p=path, y=local_dt.year, l=loc.netkeiba_id, m=local_dt.month, d=local_dt.day, n=race_number
        )
    raise ValueError(f"unknown netkeiba type: {location}")

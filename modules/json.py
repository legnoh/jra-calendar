import dataclasses
from datetime import date, time, datetime
from enum import Enum

def json_serial(obj):
    if dataclasses.is_dataclass(obj) and not isinstance(obj, type):
        return dataclasses.asdict(obj)
    if isinstance(obj, Enum):
        return obj.value
    if isinstance(obj, (datetime)):
        ts = int(round(obj.timestamp()))
        return ts
    elif isinstance(obj, (date)):
        ts = int(round(datetime.combine(obj, time()).timestamp()))
        return ts
    else:
        return obj

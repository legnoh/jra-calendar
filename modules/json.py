from datetime import date, time, datetime

def json_serial(obj):
    if isinstance(obj, (datetime)):
        ts = int(round(obj.timestamp()))
        return ts
    elif isinstance(obj, (date)):
        ts = int(round(datetime.combine(obj, time()).timestamp()))
        return ts
    else:
        return obj

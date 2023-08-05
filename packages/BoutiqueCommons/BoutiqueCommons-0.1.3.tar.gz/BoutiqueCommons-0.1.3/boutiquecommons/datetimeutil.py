import datetime


def isoformat_to_datetime(str):
  if str is None:
    return None
  return datetime.datetime.strptime(str, "%Y-%m-%dT%H:%M:%S")

def datetime_to_isoformat(datetime_obj):
  if datetime_obj is None:
    return None

  updated_s = datetime_obj.isoformat()
  return updated_s

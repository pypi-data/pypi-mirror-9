from datetime import datetime

from dateutil import tz


tzlocal = tz.tzlocal()


def now():
    return datetime.now(tz=tzlocal)

import time
import datetime


def str_to_timestamp(str_date, date_format='%Y-%m-%m %H:%M:%S'):
    return time.mktime(datetime.datetime.strptime(str_date, date_format).timetuple())

import datetime
import time


def min_click_dt():
    dt = datetime.date(day=2, year=1970, month=1)
    return int(time.mktime(dt.timetuple()))


def max_click_dt():
    dt = datetime.date(day=2, year=2100, month=1)
    return int(time.mktime(dt.timetuple()))


def progress_bar(current, total, bar_length=20):
    fraction = current / total

    arrow = int(fraction * bar_length - 1) * '-' + '>'
    padding = int(bar_length - len(arrow)) * ' '

    ending = '\n' if current == total else '\r'

    print(f'Progress: [{arrow}{padding}] {int(fraction * 100)}%', end=ending)


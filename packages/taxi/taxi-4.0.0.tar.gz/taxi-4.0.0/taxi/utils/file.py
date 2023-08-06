from __future__ import unicode_literals

import datetime


def expand_date(filename, date=None):
    if date is None:
        date = datetime.date.today()

    return date.strftime(filename)

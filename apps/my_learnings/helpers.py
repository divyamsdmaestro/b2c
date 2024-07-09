from dateutil.relativedelta import relativedelta
from django.utils.datetime_safe import datetime


def get_one_year_datetime_from_now():
    """Returns the datetime object which is one year from now."""

    return datetime.now() + relativedelta(years=1)

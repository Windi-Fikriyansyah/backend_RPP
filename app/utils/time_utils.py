import pytz
from datetime import datetime

def get_jakarta_time():
    """
    Returns the current time in Asia/Jakarta (WIB) as a naive datetime.
    """
    return datetime.now(pytz.timezone("Asia/Jakarta")).replace(tzinfo=None)

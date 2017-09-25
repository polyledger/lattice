import dateutil.parser
import datetime
import time

"""
DATETIME OBJECT CONVERSION HELPERS
"""

def current_datetime_string():
    """Returns a current datetime string"""
    return str(datetime.datetime.now())

def date_string_to_datetime(dstring):
    """Converts a date to a datetime object"""
    return timestamp_to_datetime(datetime_string_to_timestamp(dstring))

def datetime_string_to_datetime(dtstring):
    """Converts an ISO 8601 formatted string to datetime object."""
    return dateutil.parser.parse(dtstring)

def datetime_to_timestamp(dt):
    """Converts a datetime object to timestamp."""
    return int((time.mktime(dt.timetuple()) + dt.microsecond / 1000000.0))

def datetime_string_to_timestamp(dtstring):
    """Converts an ISO 8601 formatted string to timestamp."""
    return datetime_to_timestamp(datetime_string_to_datetime(dtstring))

def timestamp_to_datetime(timestamp):
    """Converts a timestamp to an ISO 8601 formatted datetime object."""
    return datetime.datetime.fromtimestamp(timestamp).isoformat()

def unix_epoch():
    """Returns a Unix epoch datetime object."""
    return datetime.datetime(1970, 1, 1)

def is_aware(dt):
    """Returns a Boolean if the datetime object is timezone aware."""
    return True if dt.tzinfo is not None and dt.tzinfo.utcoffset(dt) is not None else False

def is_naive(dt):
    """Returns a Boolean if the datetime object is timezone naive."""
    return True if dt.tzinfo is None or (dt.tzinfo is not None and dt.tzinfo.utcoffset(dt) is None) else False

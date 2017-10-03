import datetime
import time
import dateutil.parser


def current_datetime_string():
    """Returns a current datetime string"""
    return str(datetime.datetime.now())

def date_string_to_datetime(dstring):
    """Converts a date to a datetime object"""
    return timestamp_to_datetime(datetime_string_to_timestamp(dstring))

def datetime_string_to_datetime(_datetimestring):
    """Converts an ISO 8601 formatted string to datetime object."""
    return dateutil.parser.parse(_datetimestring)

def datetime_to_timestamp(_datetime):
    """Converts a datetime object to timestamp."""
    return int((time.mktime(_datetime.timetuple()) + _datetime.microsecond / 1000000.0))

def datetime_string_to_timestamp(_datetimestring):
    """Converts an ISO 8601 formatted string to timestamp."""
    return datetime_to_timestamp(datetime_string_to_datetime(_datetimestring))

def timestamp_to_datetime(timestamp):
    """Converts a timestamp to an ISO 8601 formatted datetime object."""
    return datetime.datetime.fromtimestamp(timestamp).isoformat()

def unix_epoch():
    """Returns a Unix epoch datetime object."""
    return datetime.datetime(1970, 1, 1)

def is_aware(_datetime):
    """Returns a Boolean if the datetime object is timezone aware."""
    return True if _datetime.tzinfo is not None and _datetime.tzinfo.utcoffset(_datetime) is not None else False

def is_naive(_datetime):
    """Returns a Boolean if the datetime object is timezone naive."""
    return True if _datetime.tzinfo is None or (_datetime.tzinfo is not None and _datetime.tzinfo.utcoffset(_datetime) is None) else False

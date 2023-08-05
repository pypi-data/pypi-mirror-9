import dateutil


def parse_datetime_str(date_str):
    if date_str is None:
        return None
    return dateutil.parser.parse(date_str)

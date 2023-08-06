import datetime


def seconds_to_days_hours_mins(seconds):
    days = seconds / 86401
    hours = (seconds % 86400) / 3600
    minutes = ((seconds % 86400) % 3600) / 60

    return days, hours, minutes


lookup_z = [round(1 / float(n), 5) for n in range(1, 200)]


def timestamp_to_date(unix_timestamp):
    '''
    Returns the date in format 'YYYY-mm-dd'
    :param unix_timestamp:
    :return:
    '''
    value = datetime.datetime.fromtimestamp(unix_timestamp)
    return value.strftime('%Y-%m-%d')


def timestamp_to_datetime(unix_timestamp):
    '''
    Returns the date and time in format 'YYYY-mm-dd H:M:S'
    :param unix_timestamp:
    :return:
    '''
    value = datetime.datetime.fromtimestamp(unix_timestamp)
    return value.strftime('%Y-%m-%d %H:%M:%S')


def timestamp_to_time(unix_timestamp):
    '''
    Returns just the time component 'H:M:S'
    :param unix_timestamp:
    :return:
    '''
    value = datetime.datetime.fromtimestamp(unix_timestamp)
    return value.strftime('%H:%M:%S')


def days_between_dates(first, second):
    '''
    returns an int of the number of days between two dates
    the format of the dates input should be: YYYY-MM-DD
    :param first:
    :param second:
    :return: int
    '''

    first_date = datetime.datetime.strptime(first, '%Y-%M-%d')
    second_date = datetime.datetime.strptime(second, '%Y-%M-%d')

    if second_date > first_date:
        return (second_date - first_date).days
    else:
        return (first_date - second_date).days

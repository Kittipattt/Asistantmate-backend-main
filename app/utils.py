from datetime import datetime


def validate_date_time(date_time_str):
    try:
        datetime.strptime(date_time_str, "%Y-%m-%d %H:%M:%S")
        return True
    except ValueError:
        return False

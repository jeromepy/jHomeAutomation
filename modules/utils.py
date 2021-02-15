import datetime

def get_current_timestamp():
    return datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")

def get_current_time():
    return datetime.datetime.now()

def get_current_day():
    return datetime.date.today()

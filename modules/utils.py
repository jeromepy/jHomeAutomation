import datetime

def get_current_timestamp():
    return datetime.datetime.now().strftime("%H:%M:%S %d.%m.%Y")

def get_current_time():
    return datetime.datetime.now()

def get_current_day():
    return datetime.date.today()
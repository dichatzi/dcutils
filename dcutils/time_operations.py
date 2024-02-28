<<<<<<< HEAD
import datetime
import pytz

__all__ = ["TimezoneConverter", "TimerObj"]


class TimezoneConverter:
    def __init__(self, date_string, date_string_format="", timezone="", isoformat=False):
        self.date_string = date_string
        self.date_string_format = date_string_format
        if isoformat:
            self.date = datetime.datetime.fromisoformat(date_string)
            self.timezone = self.date.tzinfo
        else:
            self.timezone = pytz.timezone(timezone)
            self.date = self.timezone.localize(datetime.datetime.strptime(self.date_string, self.date_string_format))

        # Initialize data for transformed timezone
        self.transformed_timezone = self.timezone
        self.transformed_date = self.date

    def transform_timezone(self, target_timezone):

        # Define new timezone
        self.transformed_timezone = pytz.timezone(target_timezone)

        # Change timezone
        self.transformed_date = self.date.astimezone(self.transformed_timezone)

        return self
    
    def __call__(self):
        print(f"Date object time: {self.date} [{self.date.tzinfo}] -> {self.transformed_date} [{self.transformed_date.tzinfo}]")


class TimerObj:
    def __init__(self):
        self.start = datetime.datetime.now()
        self.previous = datetime.datetime.now()

        print(f"[{self.start.strftime('%Y-%m-%d %H:%M:%S')}] Starting execution")

    def __call__(self, message=""):
        # Get current time
        self.now = datetime.datetime.now()
    
        # Get total execution
        total_execution = self.now - self.start

        # Get time delta
        time_delta = self.now - self.previous

        # Define previous time point
        self.previous = self.now

        # Print time
        print(f"[{self.now.strftime('%Y-%m-%d %H:%M:%S')}] {message} {round(time_delta.seconds/60, 2)} minutes - {round(time_delta.seconds)} seconds")



# def date_proc(obj:datetime.datetime, year=None, month=None, day=None, hour=None, minute=None, second=None, microsecond=None, tzinfo=None) -> datetime.datetime:
#     """
#     Process datetime object.

#     :param obj: The input datetime object.
#     :param year: Input year.
#     :param month: Input month.
#     :param day: Input day.
#     :param hour: Input hour.
#     :param minute: Input minute.
#     :param second: Input second.
#     :param microsecond: Input microsecond.
#     :param tzinfo: Input tzinfo.
#     :return: Output datetime object.
#     """
#     # Initialize values
#     year = year if year is not None else obj.year
#     month = month if month is not None else obj.month
#     day = day if day is not None else obj.day
#     hour = hour if hour is not None else obj.hour
#     minute = minute if minute is not None else obj.minute
#     second = second if second is not None else obj.second
#     microsecond = microsecond if microsecond is not None else obj.microsecond
#     tzinfo = tzinfo if tzinfo is not None else obj.tzinfo

#     # Create new datetime object
#     out_obj = obj.replace(year=year, month=month, day=day, hour=hour, minute=minute, second=second, microsecond=microsecond, tzinfo=tzinfo)

#     return out_obj
=======
import datetime
import pytz

__all__ = ["TimezoneConverter", "TimerObj"]


class TimezoneConverter:
    def __init__(self, date_string, date_string_format="", timezone="", isoformat=False):
        self.date_string = date_string
        self.date_string_format = date_string_format
        if isoformat:
            self.date = datetime.datetime.fromisoformat(date_string)
            self.timezone = self.date.tzinfo
        else:
            self.timezone = pytz.timezone(timezone)
            self.date = self.timezone.localize(datetime.datetime.strptime(self.date_string, self.date_string_format))

        # Initialize data for transformed timezone
        self.transformed_timezone = self.timezone
        self.transformed_date = self.date

    def transform_timezone(self, target_timezone):

        # Define new timezone
        self.transformed_timezone = pytz.timezone(target_timezone)

        # Change timezone
        self.transformed_date = self.date.astimezone(self.transformed_timezone)

        return self
    
    def __call__(self):
        print(f"Date object time: {self.date} [{self.date.tzinfo}] -> {self.transformed_date} [{self.transformed_date.tzinfo}]")


class TimerObj:
    def __init__(self):
        self.start = datetime.datetime.now()
        self.previous = datetime.datetime.now()

        print(f"[{self.start.strftime('%Y-%m-%d %H:%M:%S')}] Starting execution")

    def __call__(self, message=""):
        # Get current time
        self.now = datetime.datetime.now()
    
        # Get total execution
        total_execution = self.now - self.start

        # Get time delta
        time_delta = self.now - self.previous

        # Define previous time point
        self.previous = self.now

        # Print time
        print(f"[{self.now.strftime('%Y-%m-%d %H:%M:%S')}] {message} {round(time_delta.seconds/60, 2)} minutes - {round(time_delta.seconds)} seconds")



# def date_proc(obj:datetime.datetime, year=None, month=None, day=None, hour=None, minute=None, second=None, microsecond=None, tzinfo=None) -> datetime.datetime:
#     """
#     Process datetime object.

#     :param obj: The input datetime object.
#     :param year: Input year.
#     :param month: Input month.
#     :param day: Input day.
#     :param hour: Input hour.
#     :param minute: Input minute.
#     :param second: Input second.
#     :param microsecond: Input microsecond.
#     :param tzinfo: Input tzinfo.
#     :return: Output datetime object.
#     """
#     # Initialize values
#     year = year if year is not None else obj.year
#     month = month if month is not None else obj.month
#     day = day if day is not None else obj.day
#     hour = hour if hour is not None else obj.hour
#     minute = minute if minute is not None else obj.minute
#     second = second if second is not None else obj.second
#     microsecond = microsecond if microsecond is not None else obj.microsecond
#     tzinfo = tzinfo if tzinfo is not None else obj.tzinfo

#     # Create new datetime object
#     out_obj = obj.replace(year=year, month=month, day=day, hour=hour, minute=minute, second=second, microsecond=microsecond, tzinfo=tzinfo)

#     return out_obj
>>>>>>> b07122e (dcUtils library after the billing project)

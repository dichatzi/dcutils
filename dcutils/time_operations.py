import datetime
import pytz


class TimeObj:
    def __init__(self, date_string, date_string_format, timezone):
        self.date_string = date_string
        self.date_string_format = date_string_format
        self.timezone = pytz.timezone(timezone)
        self.date = self.timezone.localize(datetime.datetime.strptime(self.date_string, self.date_string_format))

    def transform_timezone(self, target_timezone):

        # Define new timezone
        new_timezone = pytz.timezone(target_timezone)

        # Change timezone
        self.date = self.date.astimezone(new_timezone)

        return self
    
    def __call__(self):
        print(f"Date object time: {self.date}")
        print(f"Date object timezone: {self.date.tzinfo}")


import datetime
import pytz


class TimezoneConverter:
    def __init__(self, date_string, date_string_format, timezone):
        self.date_string = date_string
        self.date_string_format = date_string_format
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
        print(f"Date object time: {self.date}")
        print(f"Date object timezone: {self.date.tzinfo}")
        print("*")
        print(f"Transformed date object time: {self.transformed_date}")
        print(f"Transformed date object timezone: {self.transformed_date.tzinfo}")


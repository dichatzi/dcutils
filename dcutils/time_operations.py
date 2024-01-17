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

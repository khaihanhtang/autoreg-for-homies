from datetime import datetime
from pytz.tzinfo import StaticTzInfo
from auto_registration_system.exception.error_maker import ErrorMaker


class TimeManager:

    def __init__(self, time_zone: StaticTzInfo, input_time_format: str, output_time_format: str):
        self._time_zone = time_zone
        self._input_time_format = input_time_format
        self._output_time_format = output_time_format

    @property
    def time_zone(self) -> StaticTzInfo:
        return self._time_zone

    @property
    def input_time_format(self) -> str:
        return self._input_time_format

    def str_to_datetime(self, datetime_str: str) -> datetime:
        return datetime.strptime(datetime_str, self._input_time_format).astimezone(tz=self._time_zone)

    def datetime_to_string(self, datetime_val: datetime) -> str:
        return datetime_val.strftime(self._output_time_format)

    def now(self) -> datetime:
        return datetime.now(self._time_zone)

    def now_to_str(self) -> str:
        return self.now().strftime(self._output_time_format)


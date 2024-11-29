from datetime import datetime
from pytz.tzinfo import StaticTzInfo


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

    def str_to_datetime(self, datetime_str: str) -> datetime or None:
        try:
            return self._time_zone.localize(datetime.strptime(datetime_str, self._input_time_format))
        except Exception:
            return None

    def datetime_to_str(self, datetime_val: datetime) -> str or None:
        try:
            return f"{datetime_val.strftime(self._output_time_format)} {datetime_val.tzinfo}"
        except Exception:
            return None

    def datetime_to_str_with_input_time_format(self, datetime_val: datetime) -> str or None:
        try:
            return datetime_val.strftime(self._input_time_format)
        except Exception:
            return None

    def now(self) -> datetime:
        return datetime.now(self._time_zone)

    def now_to_str(self) -> str:
        return self.now().strftime(self._output_time_format)


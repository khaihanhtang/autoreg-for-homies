from datetime import datetime

from pytz.tzinfo import StaticTzInfo


class TimeManager:

    def __init__(self, time_zone: StaticTzInfo, time_format: str):
        self._time_zone = time_zone
        self._time_format = time_format

    def now_to_str(self) -> str:
        return datetime.now(self._time_zone).strftime(self._time_format)

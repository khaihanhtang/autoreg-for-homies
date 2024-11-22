from auto_registration_system.data_structure.time_manager import TimeManager
from datetime import datetime

from auto_registration_system.exception.error_maker import ErrorMaker


class ReleaseTimeManager:
    def __init__(self):
        self._release_time: datetime or None = None
        self._enabled: bool = False

    @property
    def release_time(self) -> datetime or None:
        return self._release_time

    @property
    def enabled(self) -> bool:
        return self._enabled

    def disable(self):
        self._enabled = False

    def enable(self):
        self._enabled = True

    def set_release_time(self, new_release_time: datetime, time_manager: TimeManager):
        self._enabled = True
        if new_release_time is None:
            self._enabled = False
        elif new_release_time <= time_manager.now():
            self._enabled = False
            raise ErrorMaker.make_release_time_invalid_exception()
        self._release_time = new_release_time

    def is_releasable(self, time_manager: TimeManager) -> bool:
        if self._enabled and self._release_time is not None and self._release_time <= time_manager.now():
            return True
        return False

    def release_time_to_str(self, time_manager: TimeManager) -> str or None:
        return time_manager.datetime_to_str(datetime_val=self.release_time)

    def release_time_to_str_with_input_time_format(self, time_manager: TimeManager) -> str or None:
        return time_manager.datetime_to_str_with_input_time_format(datetime_val=self.release_time)

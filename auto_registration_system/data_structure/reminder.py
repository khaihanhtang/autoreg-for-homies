from auto_registration_system.exception.error_maker import ErrorMaker
from auto_registration_system.data_structure.time_manager import TimeManager
from datetime import *


class Reminder:

    def __init__(self, time_list: list[int], time_manager: TimeManager, release_time: datetime):
        if not Reminder.check_valid_time_list(time_list=time_list):
            raise ErrorMaker.make_time_list_invalid_exception()
        self._time_list: list[int] = time_list
        self._pointer: int = 1 + Reminder.determine_pointer(
            time_list=self._time_list,
            time_manager=time_manager,
            release_time=release_time
        )

    @staticmethod
    def check_valid_time_list(time_list: list[int]) -> bool:
        for value in time_list:
            if value <= 0:
                return False
        for i in range(1, len(time_list)):
            if time_list[i - 1] <= time_list[i]:
                return False
        return True

    @staticmethod
    def compute_minutes_left(time_manager: TimeManager, release_time: datetime) -> float:
        return (release_time - time_manager.now()).total_seconds() / 60

    @staticmethod
    def determine_pointer(time_list: list[int], time_manager: TimeManager, release_time: datetime) -> int:
        if release_time is None:
            return 0
        minutes_left: float = Reminder.compute_minutes_left(time_manager=time_manager, release_time=release_time)
        res = -1
        for i, val in enumerate(time_list):
            if minutes_left < float(val):
                res = i
        return res

    def update_pointer(self, time_manager: TimeManager, release_time: datetime) -> (bool, int):
        is_updated: bool = False
        to_be_reminded_minutes_left: int = -1
        try:
            minutes_left: float = Reminder.compute_minutes_left(
                time_manager=time_manager,
                release_time=release_time
            )
            while self._pointer < len(self._time_list) and minutes_left < float(self._time_list[self._pointer]):
                to_be_reminded_minutes_left = self._time_list[self._pointer]
                self._pointer += 1
                is_updated = True
        except Exception:
            pass
        return is_updated, to_be_reminded_minutes_left

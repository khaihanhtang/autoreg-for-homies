from datetime import datetime, timedelta
from enum import StrEnum

from auto_registration_system.command import Command
from auto_registration_system.data_structure.time_manager import TimeManager
from auto_registration_system.exception.error_maker import ErrorMaker


class ReleaseMode(StrEnum):
    ONCE = Command.COMMAND_NOTITIME
    WEEKLY = Command.COMMAND_WEEKLYNOTITIME


WEEK = timedelta(days=7)
PRE_RELEASE_RESET_DONE = "pre_release_reset_done"


# Tracks one active mode, its next deadline, and whether that occurrence has been prepared.
class ReleaseTimeManager:
    def __init__(self):
        self._release_time: datetime | None = None
        self._mode: ReleaseMode | None = None
        self.pre_release_reset_done = False

    @property
    def release_time(self) -> datetime | None:
        return self._release_time

    @property
    def mode(self) -> ReleaseMode | None:
        return self._mode

    @property
    def enabled(self) -> bool:
        return self._mode is not None

    def disable(self) -> None:
        self._mode = None
        self._release_time = None
        self.pre_release_reset_done = False

    def set_release_time(self, new_release_time: datetime, time_manager: TimeManager,
                         mode: ReleaseMode = ReleaseMode.ONCE) -> None:
        if new_release_time <= time_manager.now():
            raise ErrorMaker.make_release_time_invalid_exception()
        # Rescheduling the same deadline preserves its completed reset, even when switching modes.
        if new_release_time != self._release_time:
            self.pre_release_reset_done = False
        self._release_time = new_release_time
        self._mode = mode

    def is_releasable(self, time_manager: TimeManager) -> bool:
        return self._release_time is not None and self._release_time <= time_manager.now()

    def complete_release(self, time_manager: TimeManager) -> None:
        if self._mode == ReleaseMode.WEEKLY:
            self._advance_weekly_release(time_manager.now())
        else:
            self.disable()

    def _advance_weekly_release(self, now: datetime) -> None:
        # Anchor recurrence to the scheduled deadline so late callbacks and downtime cannot shift it.
        weeks_elapsed = (now - self._release_time) // WEEK
        self.pre_release_reset_done = False
        try:
            self._release_time += (weeks_elapsed + 1) * WEEK
        except OverflowError:
            self.disable()

    def release_time_to_str(self, time_manager: TimeManager) -> str | None:
        return time_manager.datetime_to_str(datetime_val=self.release_time)

    def serialize(self, time_manager: TimeManager) -> str | None:
        # A bare date is the legacy one-time format. Weekly mode adds a prefix and the reset marker has its own line.
        release_time = time_manager.datetime_to_str_with_input_time_format(self._release_time)
        if self._mode == ReleaseMode.WEEKLY:
            release_time = f"{self._mode} {release_time}"
        if self.pre_release_reset_done:
            return f"{release_time}\n{PRE_RELEASE_RESET_DONE}"
        return release_time

    def restore(self, saved_schedule: str | None, time_manager: TimeManager) -> None:
        self.disable()
        saved_schedule = (saved_schedule or "").strip()
        saved_schedule, _, saved_reset_status = saved_schedule.partition("\n")
        weekly_prefix = f"{ReleaseMode.WEEKLY} "
        weekly = saved_schedule.startswith(weekly_prefix)
        release_time = time_manager.str_to_datetime(saved_schedule.removeprefix(weekly_prefix))
        if release_time is None:
            return

        now = time_manager.now()
        # Expired one-time releases are dropped. Weekly schedules skip to the next future occurrence.
        if not weekly and release_time <= now:
            return
        self._mode = ReleaseMode.WEEKLY if weekly else ReleaseMode.ONCE
        self._release_time = release_time
        self.pre_release_reset_done = saved_reset_status == PRE_RELEASE_RESET_DONE
        if weekly and release_time < now:
            self._advance_weekly_release(now)

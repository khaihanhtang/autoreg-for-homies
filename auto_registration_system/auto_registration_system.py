from datetime import datetime, timedelta
from typing import BinaryIO

from telegram import MessageEntity

from auto_registration_system.command_handler.handler_aka import AkaHandler
from auto_registration_system.command_handler.handler_allplayable import AllpendingHandler
from auto_registration_system.data_structure.chat_manager import ChatManager
from auto_registration_system.command_handler.handler_av import AvHandler
from auto_registration_system.command_handler.handler_dereg import DeregHandler
from auto_registration_system.command_handler.handler_reg import RegHandler
from auto_registration_system.command_handler.handler_reserve import ReserveHandler
from auto_registration_system.data_structure.lock_manager import LockManager
from auto_registration_system.data_structure.registration_data import RegistrationData
from auto_registration_system.data_structure.admin_manager import AdminManager
from auto_registration_system.command_handler.handler_new import NewHandler
from auto_registration_system.data_structure.release_time_manager import ReleaseMode, ReleaseTimeManager
from auto_registration_system.exception.error_maker import ErrorMaker
from auto_registration_system.exception.exception_syntax_error import SyntaxErrorException
from auto_registration_system.term import Term
from config import Config
from string_parser.string_parser import StringParser
from auto_registration_system.data_structure.identity_manager import IdentityManager
from auto_registration_system.data_structure.time_manager import TimeManager
from data_handler.data_handler import DataHandler
from auto_registration_system.data_structure.reminder import Reminder
from tracer import Tracer


# Owns list and release state. The Telegram adapter handles message delivery and timers.
class AutoRegistrationSystem:

    def __init__(self, admins: set[str], identity_manager: IdentityManager, time_manager: TimeManager):
        self._data: RegistrationData or None = None
        self._pre_released_data: RegistrationData or None = None
        self._admin_manager: AdminManager = AdminManager(admins=admins)
        self._lock_manager: LockManager = LockManager(locked=False)
        self._identity_manager: IdentityManager = identity_manager
        self._release_time_manager: ReleaseTimeManager = ReleaseTimeManager()
        self._reset_reminder(time_manager)

    def _reset_reminder(self, time_manager: TimeManager) -> None:
        self._reminder: Reminder = Reminder(
            time_list=Config.reminder_time_list,
            time_manager=time_manager,
            release_time=self._release_time_manager.release_time
        )

    def attempt_release_data(self, time_manager: TimeManager) -> bool:
        if not self._release_time_manager.is_releasable(time_manager):
            return False
        # If the staged list is absent, a weekly occurrence keeps the active list and advances the deadline.
        publish = self._release_time_manager.mode == ReleaseMode.ONCE or self._pre_released_data is not None
        if publish:
            self._data = self._pre_released_data
            self._pre_released_data = None
        self._release_time_manager.complete_release(time_manager)
        self._reset_reminder(time_manager)
        return publish

    def update_reminder(self, time_manager: TimeManager) -> (bool, int):
        is_updated, minutes_left = self._reminder.update_pointer(
            time_manager=time_manager,
            release_time=self._release_time_manager.release_time
        )
        if self._release_time_manager.mode == ReleaseMode.WEEKLY and self._pre_released_data is None:
            return False, -1
        return is_updated, minutes_left

    def next_release_check(self) -> datetime | None:
        # A single timer wakes at the earliest pending reset, reminder, or release.
        release_time = self._release_time_manager.release_time
        if release_time is None:
            return None
        reminder_or_release = self._reminder.next_time(release_time)
        reset_time = self._pre_release_reset_time()
        return min(reminder_or_release, reset_time) if reset_time is not None else reminder_or_release

    def _pre_release_reset_time(self) -> datetime | None:
        manager = self._release_time_manager
        if manager.release_time is None or manager.pre_release_reset_done or Config.pre_release_reset_minutes <= 0:
            return None
        # A weekly reset becomes eligible once a replacement list is staged.
        if manager.mode == ReleaseMode.WEEKLY and self._pre_released_data is None:
            return None
        return manager.release_time - timedelta(minutes=Config.pre_release_reset_minutes)

    def attempt_pre_release_reset(self, time_manager: TimeManager) -> bool:
        reset_time = self._pre_release_reset_time()
        release_time = self._release_time_manager.release_time
        # The preparation window begins at the configured lead time and ends at release.
        if reset_time is None or not reset_time <= time_manager.now() < release_time:
            return False
        self._reset_active_list()
        self._lock_manager.locked = False
        # Save this marker with the schedule so a restart inside the window cannot repeat the reset.
        self._release_time_manager.pre_release_reset_done = True
        return True

    def restore_release_schedule(self, saved_schedule: str | None, time_manager: TimeManager) -> None:
        self._release_time_manager.restore(saved_schedule, time_manager)
        self._reset_reminder(time_manager)

    @property
    def release_time_manager(self) -> ReleaseTimeManager:
        return self._release_time_manager

    @property
    def data(self) -> RegistrationData:
        return self._data

    @property
    def identity_manager(self) -> IdentityManager:
        return self._identity_manager

    @staticmethod
    def convert_registrations_to_string(data: RegistrationData or None) -> str or None:
        if data is None or not data.bookings_by_date_venue:
            return None
        res = ""
        for date_venue_name, date_venue_data in data.bookings_by_date_venue.items():
            res += f"{Term.DATE_VENUE} {date_venue_name}\n"
            for slot_label, slot in date_venue_data.items():
                res += slot.to_string(slot_label=slot_label)
        return res

    @staticmethod
    def convert_counts_from_available_slots_to_string(data: RegistrationData) -> str or None:
        if data is None:
            return None
        res = ""
        for date_venue_name, date_venue_data in data.bookings_by_date_venue.items():
            res += f"{Term.DATE_VENUE} {date_venue_name}\n"
            for slot_label, slot in date_venue_data.items():
                res += f"{Term.INDENT_SPACE}[{slot_label}] Need {slot.get_num_available()} additional players.\n"
        return res

    def handle_reset(self, username: str) -> str:
        try:
            self._admin_manager.enforce_admin(username=username)
        except Exception as e:
            return repr(e)

        self._reset_active_list()
        return "The entire list has been deleted!"

    def _reset_active_list(self) -> None:
        if self._data is not None:
            self._data.reset()

    def handle_all(self, username: str, chat_id: int):
        # Members can view the active list in allowed chats. Admins can view the staged list elsewhere.
        try:
            ChatManager.enforce_chat_id(chat_id=chat_id, allowed_chat_ids=Config.allowed_chat_ids)
        except Exception:
            try:
                self._admin_manager.enforce_admin(username=username)
            except Exception:
                raise ErrorMaker.make_admin_permission_error_exception()

    def handle_new(self, username: str, message: str, chat_id: int) -> (str, bool):
        is_in_main_group = ChatManager.is_chat_id_allowed(chat_id=chat_id, allowed_chat_ids=Config.allowed_chat_ids)
        try:
            self._admin_manager.enforce_admin(username=username)
        except Exception as e:
            return repr(e), is_in_main_group

        try:
            # Parse the whole list in a temporary object before replacing the active or staged list.
            temp_data = self._parse_list(message)
            if temp_data is not None:
                if is_in_main_group:
                    self._data = temp_data
                else:
                    self._pre_released_data = temp_data
                return "Set up successfully!", is_in_main_group
            return "Nothing has been changed", is_in_main_group
        except Exception as e:
            return repr(e), is_in_main_group

    @staticmethod
    def _parse_list(message: str | None) -> RegistrationData | None:
        if not message:
            return None
        data = RegistrationData()
        if NewHandler.handle(message=message, data=data, max_num_players=Config.max_num_players_per_slot):
            return data
        return None

    def handle_notitime(self, username: str, message: str, time_manager: TimeManager,
                        mode: ReleaseMode = ReleaseMode.ONCE) -> tuple[bool, str]:
        # Both commands share one schedule. The Boolean tells the adapter whether to save and requeue it.
        manager = self._release_time_manager
        try:
            self._admin_manager.enforce_admin(username=username)
            args = message.split()
            if args and args[0].startswith("/"):
                args = args[1:]
            if not args:
                # A bare command cancels its own mode and leaves the other mode active.
                if manager.mode != mode:
                    return False, f"/{mode} is already off."
                manager.disable()
                self._reset_reminder(time_manager)
                return True, f"/{mode} is now off."

            release_time = time_manager.str_to_datetime(" ".join(args))
            if release_time is None:
                return False, f"Use /{mode} HH:MM:SS DD/MM/YYYY in Singapore time."
            manager.set_release_time(release_time, time_manager, mode)
            self._reset_reminder(time_manager)
            scheduled_time = manager.release_time_to_str(time_manager)
            if mode == ReleaseMode.WEEKLY:
                return True, f"✅ Weekly releases start on {scheduled_time} and repeat every 7 days."
            return True, f"✅ New list will be released on {scheduled_time}."
        except Exception as e:
            return False, repr(e)

    def handle_state(self, time_manager: TimeManager) -> str:
        # Any chat can request this summary of the lock, active list and next release.
        lock_status = "locked" if self._lock_manager.locked else "unlocked"
        has_list = self._data is not None and bool(self._data.bookings_by_date_venue)
        list_status = "has information" if has_list else "is empty"
        manager = self._release_time_manager
        state = f"System is {lock_status}.\nActive list {list_status}."
        if not manager.enabled:
            return f"{state}\nRelease schedule is off."
        return (f"{state}\n/{manager.mode} is active.\n"
                f"Next release on {manager.release_time_to_str(time_manager)}.")

    def get_all_slots_as_string(self, is_main_data: bool = True) -> str or None:
        data = self._data
        if not is_main_data:
            data = self._pre_released_data
        return AutoRegistrationSystem.convert_registrations_to_string(data=data)

    def get_available_slots_as_string(self) -> str:
        res: str = AutoRegistrationSystem.convert_counts_from_available_slots_to_string(
            data=AvHandler.handle(data=self._data)
        )
        if res is None or len(res) == 0:
            return "There is no available slot!"
        return res

    def write_all_data_to_files(self, data_handler: DataHandler, time_manager: TimeManager):
        # Save the lists, lock and schedule as one snapshot so they represent the same update.
        data_handler.write_state({
            "locked": self._lock_manager.locked,
            "active_list": self._data.to_state() if self._data is not None else None,
            "staged_list": self._pre_released_data.to_state() if self._pre_released_data is not None else None,
            "release_schedule": self._release_time_manager.serialize(time_manager),
        })

    def load_saved_state(self, data_handler: DataHandler, time_manager: TimeManager) -> None:
        state = data_handler.read_state()
        if state is None:
            # The older text files contain the lists and release time. Their initial lock state is unlocked.
            active_list, release_schedule, staged_list = data_handler.read_legacy_state()
            self._data = self._parse_list(active_list)
            self._pre_released_data = self._parse_list(staged_list)
            self._lock_manager.locked = False
        else:
            self._data = RegistrationData.from_state(state["active_list"])
            self._pre_released_data = RegistrationData.from_state(state["staged_list"])
            self._lock_manager.locked = state["locked"]
            release_schedule = state["release_schedule"]
        self.restore_release_schedule(release_schedule, time_manager)

    def handle_register(self, command_string_for_suggestion: str, username: str, message: str, chat_id: int) \
            -> (str, str or None):
        try:
            self._lock_manager.enforce_system_unlocked(username=username, admin_manager=self._admin_manager)
            ChatManager.enforce_chat_id(chat_id=chat_id, allowed_chat_ids=Config.allowed_chat_ids)
            StringParser.enforce_single_line_message(message=message)
            response, conflict_names, slot_label = RegHandler.handle(message=message, data=self._data)

            if conflict_names is not None:
                suggestion = RegHandler.make_suggestion(
                    command_string=command_string_for_suggestion,
                    id_strings=conflict_names,
                    slot_label=slot_label
                )
                return response, suggestion
            return response, None
        except Exception as e:
            return repr(e), None

    def handle_reserve(self, username: str, message: str, chat_id: int) -> str:
        try:
            self._lock_manager.enforce_system_unlocked(username=username, admin_manager=self._admin_manager)
            ChatManager.enforce_chat_id(chat_id=chat_id, allowed_chat_ids=Config.allowed_chat_ids)
            StringParser.enforce_single_line_message(message=message)
            return ReserveHandler.handle(message=message, data=self._data)
        except Exception as e:
            return repr(e)

    def handle_deregister(self, command_string: str, username: str, id_string: str, message: str, chat_id: int) -> str:
        try:
            self._lock_manager.enforce_system_unlocked(username=username, admin_manager=self._admin_manager)
            ChatManager.enforce_chat_id(chat_id=chat_id, allowed_chat_ids=Config.allowed_chat_ids)
            StringParser.enforce_single_line_message(message=message)
            return DeregHandler.handle(message=message, data=self._data)
        except SyntaxErrorException:
            response: str = "Syntax error\\!"
            suggestion: str = DeregHandler.make_suggestion(
                command_string=command_string,
                id_string=id_string,
                data=self._data
            )
            if suggestion is not None:
                return f"{response}\n{suggestion}"
            return response
        except Exception as e:
            return repr(e)

    def get_admin_list_as_string(self) -> str:
        return str(self._admin_manager.admins)

    def handle_allpending(self, username: str, chat_id: int) -> str:
        try:
            ChatManager.enforce_chat_id(chat_id=chat_id, allowed_chat_ids=Config.allowed_chat_ids)
            self._admin_manager.enforce_admin(username=username)
        except Exception as e:
            return repr(e)

        try:
            return AllpendingHandler.handle(data=self._data)
        except Exception as e:
            return repr(e)

    def handle_lock(self, username: str) -> str:
        try:
            self._admin_manager.enforce_admin(username=username)
            self._lock_manager.locked = True
            return "The system has been locked!"
        except Exception as e:
            return repr(e)

    def handle_unlock(self, username: str) -> str:
        try:
            self._admin_manager.enforce_admin(username=username)
            self._lock_manager.locked = False
            return "The system has been unlocked!"
        except Exception as e:
            return repr(e)

    def handle_history(self, username: str, tracer: Tracer) -> BinaryIO:
        self._admin_manager.enforce_admin(username=username)
        return tracer.load_file_history()

    def handle_aka(self, sender_id: int, sender_full_name: str, message: str,
                   message_entities: dict[MessageEntity, str]) -> str:
        if len(message_entities) >= 1:
            # self._admin_manager.enforce_admin(username=sender_username)
            raise ErrorMaker.make_syntax_error_exception(message=message)
        return AkaHandler.handle(
            sender_id=sender_id,
            sender_full_name=sender_full_name,
            message=message,
            message_entities=message_entities,
            identity_manager=self._identity_manager
        )

from typing import BinaryIO

from telegram import MessageEntity

from auto_registration_system.command_handler.handle_aka import AkaHandler
from auto_registration_system.data_structure.chat_manager import ChatManager
from auto_registration_system.command_handler.handler_allplayable import AllplayableHandler
from auto_registration_system.command_handler.handler_av import AvHandler
from auto_registration_system.command_handler.handler_dereg import DeregHandler
from auto_registration_system.command_handler.handler_reg import RegHandler
from auto_registration_system.command_handler.handler_reserve import ReserveHandler
from auto_registration_system.data_structure.lock_manager import LockManager
from auto_registration_system.data_structure.registration_data import RegistrationData
from auto_registration_system.data_structure.admin_manager import AdminManager
from auto_registration_system.command_handler.handler_new import NewHandler
from auto_registration_system.exception.error_maker import ErrorMaker
from auto_registration_system.exception.exception_syntax_error import SyntaxErrorException
from auto_registration_system.term import Term
from string_parser.string_parser import StringParser
from auto_registration_system.data_structure.identity_manager import IdentityManager
from datetime import datetime
from auto_registration_system.data_structure.time_manager import TimeManager
from data_handler.data_handler import DataHandler


class AutoRegistrationSystem:

    class ReleaseTimeManager:
        def __init__(self, time_manager: TimeManager):
            self._time_manager: TimeManager = time_manager
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

        @release_time.setter
        def release_time(self, new_release_time: datetime):
            self._release_time = new_release_time
            self._enabled = True
            if new_release_time <= self._time_manager.now():
                self._enabled = False
                raise ErrorMaker.make_release_time_invalid_exception()

        def is_releasable(self) -> bool:
            if self._enabled and self._release_time is not None and self._release_time <= self._time_manager.now():
                return True
            return False

        def release_time_to_str(self) -> str or None:
            return self._time_manager.datetime_to_str(datetime_val=self.release_time)

        def release_time_to_str_with_input_time_format(self) -> str or None:
            return self._time_manager.datetime_to_str_with_input_time_format(datetime_val=self.release_time)

    def __init__(self, admins: set[str], chat_ids: set[int], alias_file_name: str, time_manager: TimeManager):
        self._data: RegistrationData or None = None
        self._pre_released_data: RegistrationData or None = None
        self._admin_manager: AdminManager = AdminManager(admins=admins)
        self._chat_manager: ChatManager = ChatManager(chat_ids=chat_ids)
        self._lock_manager: LockManager = LockManager(locked=False)
        self._identity_manager: IdentityManager = IdentityManager(alias_file_name=alias_file_name)
        self._release_time_manager: AutoRegistrationSystem.ReleaseTimeManager \
            = AutoRegistrationSystem.ReleaseTimeManager(time_manager=time_manager)

    def attempt_release_data(self) -> bool:
        if self._release_time_manager.is_releasable():
            self._data = self._pre_released_data
            self._pre_released_data = None
            self._release_time_manager.disable()
            return True
        return False

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
        if data is None:
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
                res += f"{Term.INDENT_SPACE}[{slot_label}] Còn thiếu {slot.get_num_available()} người.\n"
        return res

    def handle_reset(self, username: str) -> str:
        try:
            self._admin_manager.enforce_admin(username=username)
        except Exception as e:
            return repr(e)

        self._data.reset()
        return "Đã xóa toàn bộ danh sách!"

    def handle_new(self, username: str, message: str, chat_id: int) -> (str, bool):
        is_in_main_group = True
        try:
            self._admin_manager.enforce_admin(username=username)
        except Exception as e:
            return repr(e), is_in_main_group

        temp_data = RegistrationData()
        try:
            response = NewHandler.handle(message=message, data=temp_data)
            if response:
                if chat_id in self._chat_manager.chat_ids:
                    self._data = temp_data
                else:
                    self._pre_released_data = temp_data
                    is_in_main_group = False
                return "Cài đặt thành công!", is_in_main_group
            return "Không có gì thay đổi", is_in_main_group
        except Exception as e:
            return repr(e), is_in_main_group

    def handle_notitime(self, username: str, message: str, time_manager: TimeManager) -> str:
        try:
            self._admin_manager.enforce_admin(username=username)
            message = StringParser.remove_command(message=message)
            self._release_time_manager.release_time = time_manager.str_to_datetime(message)
            return f"Release time is set to be {time_manager.datetime_to_str(
                self._release_time_manager.release_time
            )}"
        except Exception as e:
            return repr(e)

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
            return "Không còn slot trống!"
        return res

    def write_all_data_to_files(self, data_handler: DataHandler):
        data_handler.write_data_to_files(
            main_list_as_str=self.get_all_slots_as_string(is_main_data=True),
            release_time_as_str=self._release_time_manager.release_time_to_str_with_input_time_format(),
            pre_released_list_as_str=self.get_all_slots_as_string(is_main_data=False)
        )

    def handle_register(self, command_string_for_suggestion: str, username: str, message: str, chat_id: int) \
            -> (str, str or None):
        try:
            self._lock_manager.enforce_system_unlocked(username=username, admin_manager=self._admin_manager)
            self._chat_manager.enforce_chat_id(chat_id=chat_id)
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
            self._chat_manager.enforce_chat_id(chat_id=chat_id)
            StringParser.enforce_single_line_message(message=message)
            return ReserveHandler.handle(message=message, data=self._data)
        except Exception as e:
            return repr(e)

    def handle_deregister(self, command_string: str, username: str, id_string: str, message: str, chat_id: int) -> str:
        try:
            self._lock_manager.enforce_system_unlocked(username=username, admin_manager=self._admin_manager)
            self._chat_manager.enforce_chat_id(chat_id=chat_id)
            StringParser.enforce_single_line_message(message=message)
            return DeregHandler.handle(message=message, data=self._data)
        except SyntaxErrorException:
            response: str = "Lỗi cú pháp\\!"
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

    def handle_allplayable(self, username: str, chat_id: int) -> str:
        try:
            self._chat_manager.enforce_chat_id(chat_id=chat_id)
            self._admin_manager.enforce_admin(username=username)
        except Exception as e:
            return repr(e)

        try:
            return AllplayableHandler.handle(data=self._data)
        except Exception as e:
            return repr(e)

    def handle_lock(self, username: str) -> str:
        try:
            self._admin_manager.enforce_admin(username=username)
            self._lock_manager.locked = True
            return "Hệ thống đã bị khóa!"
        except Exception as e:
            return repr(e)

    def handle_unlock(self, username: str) -> str:
        try:
            self._admin_manager.enforce_admin(username=username)
            self._lock_manager.locked = False
            return "Hệ thống đã được mở khóa!"
        except Exception as e:
            return repr(e)

    def handle_history(self, username: str, history_file_name: str) -> BinaryIO:
        self._admin_manager.enforce_admin(username=username)
        return open(history_file_name, 'rb')

    def handle_aka(self, sender_id: int, sender_full_name: str, message: str, command_string: str,
                   message_entities: dict[MessageEntity, str]) -> str:
        if len(message_entities) >= 1:
            # self._admin_manager.enforce_admin(username=sender_username)
            raise ErrorMaker.make_syntax_error_exception(message=message)
        return AkaHandler.handle(
            sender_id=sender_id,
            sender_full_name=sender_full_name,
            message=message,
            command_string=command_string,
            message_entities=message_entities,
            identity_manager=self._identity_manager
        )

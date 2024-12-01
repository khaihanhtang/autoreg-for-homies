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
from auto_registration_system.data_structure.release_time_manager import ReleaseTimeManager
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


class AutoRegistrationSystem:

    def __init__(self, admins: set[str], identity_manager: IdentityManager, time_manager: TimeManager):
        self._data: RegistrationData or None = None
        self._pre_released_data: RegistrationData or None = None
        self._admin_manager: AdminManager = AdminManager(admins=admins)
        self._lock_manager: LockManager = LockManager(locked=False)
        self._identity_manager: IdentityManager = identity_manager
        self._release_time_manager: ReleaseTimeManager = ReleaseTimeManager()
        self._reminder: Reminder = Reminder(
            time_list=Config.reminder_time_list,
            time_manager=time_manager,
            release_time=self._release_time_manager.release_time
        )

    def attempt_release_data(self, time_manager: TimeManager) -> bool:
        if self._release_time_manager.is_releasable(time_manager=time_manager):
            self._data = self._pre_released_data
            self._pre_released_data = None
            self._release_time_manager.disable()
            return True
        return False

    def update_reminder(self, time_manager: TimeManager) -> (bool, int):
        return self._reminder.update_pointer(
            time_manager=time_manager,
            release_time=self._release_time_manager.release_time
        )

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
                res += f"{Term.INDENT_SPACE}[{slot_label}] Need {slot.get_num_available()} additional players.\n"
        return res

    def handle_reset(self, username: str) -> str:
        try:
            self._admin_manager.enforce_admin(username=username)
        except Exception as e:
            return repr(e)

        self._data.reset()
        return "The entire list has been deleted!"

    def handle_all(self, username: str, chat_id: int):
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

        temp_data = RegistrationData()
        try:
            response = NewHandler.handle(
                message=message,
                data=temp_data,
                max_num_players=Config.max_num_players_per_slot
            )
            if response:
                if is_in_main_group:
                    self._data = temp_data
                else:
                    self._pre_released_data = temp_data
                return "Set up successfully!", is_in_main_group
            return "Nothing has been changed", is_in_main_group
        except Exception as e:
            return repr(e), is_in_main_group

    def handle_notitime(self, username: str, message: str, time_manager: TimeManager) -> (bool, str):
        try:
            self._admin_manager.enforce_admin(username=username)
            message = StringParser.remove_command(message=message)
            self._release_time_manager.set_release_time(
                new_release_time=time_manager.str_to_datetime(message),
                time_manager=time_manager
            )
            self._reminder = Reminder(
                time_list=Config.reminder_time_list,
                time_manager=time_manager,
                release_time=self._release_time_manager.release_time
            )
            if not self.release_time_manager.enabled:
                return False, f"❌ Release time hasn't been set!"
            return True, f"✅ New list will be released after {time_manager.datetime_to_str(
                self._release_time_manager.release_time
            )}"
        except Exception as e:
            return False, repr(e)

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
        data_handler.write_data_to_files(
            main_list_as_str=self.get_all_slots_as_string(is_main_data=True),
            release_time_as_str=self._release_time_manager.release_time_to_str_with_input_time_format(
                time_manager=time_manager
            ),
            pre_released_list_as_str=self.get_all_slots_as_string(is_main_data=False)
        )

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

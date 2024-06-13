from typing import BinaryIO

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
from auto_registration_system.term import Term
from string_parser.string_parser import StringParser


class AutoRegistrationSystem:

    def __init__(self, admins: set[str], chat_ids: set[int]):
        self._data: RegistrationData or None = None
        self._admin_manager: AdminManager = AdminManager(admins=admins)
        self._chat_manager: ChatManager = ChatManager(chat_ids=chat_ids)
        self._lock_manager: LockManager = LockManager(locked=False)

    @property
    def data(self) -> RegistrationData:
        return self._data

    @staticmethod
    def convert_registrations_to_string(data: RegistrationData) -> str or None:
        if data is None:
            return None
        res = ""
        for date_venue_name, date_venue_data in data.bookings_by_date_venue.items():
            res += f"{Term.DATE_VENUE} {date_venue_name}\n"
            for slot_label, slot_data in date_venue_data.items():
                res += f"[{slot_label}] {slot_data.slot_name}, {Term.NUM_PLAYERS} {slot_data.max_num_players}\n"
                for i in range(slot_data.max_num_players):
                    res += f"   {i + 1}."
                    if i < len(slot_data.players) and slot_data.players[i] is not None:
                        res += f" {slot_data.players[i]}"
                    res += "\n"
                for reservation in slot_data.reservations:
                    res += f"   {Term.RESERVATION}. {reservation.name}"
                    if reservation.is_playable:
                        res += f" {Term.PLAYABLE}"
                    res += "\n"
        return res

    def handle_new(self, username: str, message: str) -> str:
        try:
            self._admin_manager.enforce_admin(username=username)
        except Exception as e:
            return repr(e)

        temp_data = RegistrationData()
        try:
            response = NewHandler.handle(message=message, data=temp_data)
            if response:
                self._data = temp_data
                return "Cài đặt thành công!"
            return "Không có gì thay đổi"
        except Exception as e:
            return repr(e)

    def get_all_slots_as_string(self) -> str or None:
        return AutoRegistrationSystem.convert_registrations_to_string(data=self._data)

    def get_available_slots_as_string(self) -> str:
        res: str = AutoRegistrationSystem.convert_registrations_to_string(
            data=AvHandler.handle(data=self._data)
        )
        if res is None or len(res) == 0:
            return "Không còn slot trống!"
        return res

    def handle_reg(self, username: str, message: str, chat_id: int) -> str:
        try:
            self._lock_manager.enforce_system_unlocked(username=username, admin_manager=self._admin_manager)
            self._chat_manager.enforce_chat_id(chat_id=chat_id)
            StringParser.enforce_single_line_message(message=message)
            return RegHandler.handle(message=message, data=self._data)
        except Exception as e:
            return repr(e)

    def handle_reserve(self, username: str, message: str, chat_id: int) -> str:
        try:
            self._lock_manager.enforce_system_unlocked(username=username, admin_manager=self._admin_manager)
            self._chat_manager.enforce_chat_id(chat_id=chat_id)
            StringParser.enforce_single_line_message(message=message)
            return ReserveHandler.handle(message=message, data=self._data)
        except Exception as e:
            return repr(e)

    def handle_deregister(self, username: str, message: str, chat_id: int) -> str:
        try:
            self._lock_manager.enforce_system_unlocked(username=username, admin_manager=self._admin_manager)
            self._chat_manager.enforce_chat_id(chat_id=chat_id)
            StringParser.enforce_single_line_message(message=message)
            return DeregHandler.handle(message=message, data=self._data)
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

    def handle_aka(self, username: str, message: str) -> str:
        pass

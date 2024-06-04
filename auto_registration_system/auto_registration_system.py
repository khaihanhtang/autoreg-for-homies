from .command_handler.handler_allplayable import AllplayableHandler
from .command_handler.handler_av import AvHandler
from .command_handler.handler_dereg import DeregHandler
from .command_handler.handler_reg import RegHandler
from .command_handler.handler_reserve import ReserveHandler
from .data_structure.registration_data import RegistrationData
from .data_structure.admin_manager import AdminManager
from .command_handler.handler_new import NewHandler
from .term import Term
from .string_parser.string_parser import StringParser


class AutoRegistrationSystem:

    def __init__(self):
        self._data: RegistrationData or None = None

    @property
    def data(self):
        return self._data

    @staticmethod
    def convert_registrations_to_string(data: RegistrationData) -> str or None:
        if data is None:
            return None
        res = ""
        for date_venue_name, date_venue_data in data.bookings_by_datevenue.items():
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
            AdminManager.enforce_admin(username=username)
        except Exception as e:
            return repr(e)

        temp_data = RegistrationData()
        try:
            message = StringParser.remove_command(message=message)
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

    def handle_reg(self, message: str) -> str:
        try:
            StringParser.enforce_single_line_message(message=message)
            message = StringParser.remove_command(message=message)
            return RegHandler.handle(message=message, data=self._data)
        except Exception as e:
            return repr(e)

    def handle_reserve(self, message: str) -> str:
        try:
            StringParser.enforce_single_line_message(message=message)
            message = StringParser.remove_command(message=message)
            return ReserveHandler.handle(message=message, data=self._data)
        except Exception as e:
            return repr(e)

    def handle_dereg(self, message: str) -> str:
        try:
            StringParser.enforce_single_line_message(message=message)
            message = StringParser.remove_command(message=message)
            return DeregHandler.handle(message=message, data=self._data)
        except Exception as e:
            return repr(e)

    @staticmethod
    def get_admin_list_as_string() -> str:
        return str(AdminManager.admin_list)

    def handle_allplayable(self, username: str, message: str) -> str:
        try:
            AdminManager.enforce_admin(username=username)
        except Exception as e:
            return repr(e)

        try:
            return AllplayableHandler.handle(message=message, data=self._data)
        except Exception as e:
            return repr(e)

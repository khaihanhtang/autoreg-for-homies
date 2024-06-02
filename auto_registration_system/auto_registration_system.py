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
        self._data: RegistrationData = None

    @staticmethod
    def convert_registrations_to_string(data: RegistrationData):
        if data is None:
            return "Registration list is empty!"
        res = ""
        for datevenue_name, datevenue_data in data.bookings_by_datevenue.items():
            res += f"{Term.DATE_VENUE} {datevenue_name}\n"
            for slot_label, slot_data in datevenue_data.items():
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

    def _retrieve(self) -> str:
        return AutoRegistrationSystem.convert_registrations_to_string(data=self._data)

    def _get_available_slots(self) -> str:
        res: str = AutoRegistrationSystem.convert_registrations_to_string(
            data=AvHandler.handle(data=self._data)
        )
        if len(res) == 0:
            return "No available slot!"
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
                return "Setup successfully!"
            return "Nothing was processed!"
        except Exception as e:
            return repr(e)

    def handle_retrieve(self, username: str, message: str) -> str:
        return self._retrieve()

    def handle_av(self, username: str, message: str) -> str:
        return self._get_available_slots()

    def handle_reg(self, username: str, message: str) -> str:
        try:
            StringParser.enforce_single_line_message(message=message)
            message = StringParser.remove_command(message=message)
            return RegHandler.handle(message=message, data=self._data)
        except Exception as e:
            return repr(e)

    def handle_reserve(self, username: str, message: str) -> str:
        try:
            StringParser.enforce_single_line_message(message=message)
            message = StringParser.remove_command(message=message)
            return ReserveHandler.handle(message=message, data=self._data)
        except Exception as e:
            return repr(e)

    def handle_dereg(self, username: str, message: str) -> str:
        try:
            StringParser.enforce_single_line_message(message=message)
            message = StringParser.remove_command(message=message)
            return DeregHandler.handle(message=message, data=self._data)
        except Exception as e:
            return repr(e)

    def handle_admin(self, username: str, message: str) -> str:
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

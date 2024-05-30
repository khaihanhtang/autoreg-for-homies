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

    def _retrieve(self) -> str:
        if self._data is None:
            return "There is no registration for registering"
        res = ""
        for datevenue_name, datevenue_data in self._data.bookings_by_datevenue.items():
            res += f"{Term.DATE_VENUE} {datevenue_name}\n"
            for slot_label, slot_data in datevenue_data.items():
                res += f"[{slot_label}] {slot_data.slot_name}, {Term.NUM_PLAYERS} {slot_data.max_num_players}\n"
                for i in range(slot_data.max_num_players):
                    res += f"   {i + 1}."
                    if i < len(slot_data.players) and slot_data.players[i] is not None:
                        res += f"     {slot_data.players[i]}"
                    res += "\n"
                for name in slot_data.reservations:
                    res += f"   {Term.RESERVATION}. {name}\n"
        return res

    def handle_new(self, username: str, message: str) -> str:
        try:
            AdminManager.enforce_admin(username=username)
        except Exception as e:
            return e.message
        self._data = RegistrationData()

        try:
            message = StringParser.remove_command(message=message)
            NewHandler.handle(message=message, data=self._data)
        except Exception as e:
            return repr(e)
        return self._retrieve()

    def handle_retrieve(self, username: str, message: str) -> str:
        return self._retrieve()

    def handle_reg(self, username: str, message: str) -> str:
        try:
            message = StringParser.remove_command(message=message)
            RegHandler.handle(message=message, data=self._data)
        except Exception as e:
            return repr(e)
        return self._retrieve()

    def handle_reserve(self, username: str, message: str) -> str:
        try:
            message = StringParser.remove_command(message=message)
            ReserveHandler.handle(message=message, data=self._data)
        except Exception as e:
            return repr(e)
        return self._retrieve()

    def handle_dereg(self, username: str, message: str) -> str:
        try:
            message = StringParser.remove_command(message=message)
            DeregHandler.handle(message=message, data=self._data)
        except Exception as e:
            return repr(e)
        return self._retrieve()

    def handle_admin(self, username: str, message: str) -> str:
        return str(AdminManager.admin_list)
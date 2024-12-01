from auto_registration_system.data_structure.registration_data import RegistrationData
from auto_registration_system.exception.error_maker import ErrorMaker
from string_parser.string_parser import StringParser


class ReserveHandler:
    @staticmethod
    def handle(message: str, data: RegistrationData) -> str:
        original_message = message
        message = StringParser.remove_command(message=message)
        try:
            slot_label = StringParser.get_last_word(message=message)
            current_message = StringParser.remove_last_word(message=message)
        except Exception:
            raise ErrorMaker.make_syntax_error_exception(message=original_message)

        players: list[str] = StringParser.split_names(current_message)

        response: str = ""
        count_processed: int = 0
        for name in players:
            if len(name) > 0:
                count_processed += 1
                try:
                    StringParser.enforce_message_containing_alpha(message=name)
                    data.reserve_player(slot_label=slot_label, player=name)
                    response += f"{name} has been inserted into reserve list of slot {slot_label}.\n"
                except Exception as e:
                    response += f"{repr(e)}\n"
        if count_processed == 0:
            return "There is nothing changed!"

        return response

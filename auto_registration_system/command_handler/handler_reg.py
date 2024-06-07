from auto_registration_system.data_structure.registration_data import RegistrationData
from auto_registration_system.exception.error_maker import ErrorMaker
from auto_registration_system.string_parser.string_parser import StringParser


class RegHandler:
    @staticmethod
    def handle(message: str, data: RegistrationData) -> str:
        try:
            slot_label = StringParser.get_last_word(message=message)
            current_message = StringParser.remove_last_word(message=message)
        except Exception:
            raise ErrorMaker.make_syntax_error_exception(message=message)

        players: list[str] = StringParser.split_names(current_message)

        response: str = ""
        count_processed: int = 0
        for name in players:
            if len(name) > 0:
                count_processed += 1
                try:
                    StringParser.enforce_message_containing_alpha(message=name)
                    data.register_player(slot_label=slot_label, player=name)
                    response += f"{name} vừa được thêm vào slot {slot_label}\n"
                except Exception as e:
                    response += f"{repr(e)}\n"
        if count_processed == 0:
            return "Không có gì thay đổi"

        data.move_all_playable_players()

        return response

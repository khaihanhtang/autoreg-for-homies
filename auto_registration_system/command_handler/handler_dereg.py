from auto_registration_system.data_structure.registration_data import RegistrationData
from auto_registration_system.string_parser.string_parser import StringParser
from ..exception.error_maker import ErrorMaker


class DeregHandler:
    @staticmethod
    def handle(message: str, data: RegistrationData):
        try:
            slot_label = StringParser.get_last_word(message=message)
            current_message = StringParser.remove_last_word(message=message)
        except:
            raise ErrorMaker.make_syntax_error_exception(message=message)

        players: list[str] = StringParser.split_names(current_message)

        response: str = ""
        count_processed: int = 0
        for name in players:
            if len(name) > 0:
                count_processed += 1
                try:
                    data.deregister_player(slot_label=slot_label, player=name)
                    response += f"{name} vừa được xóa khỏi slot {slot_label}\n"
                except Exception as e:
                    response += f"{repr(e)}\n"
        if count_processed == 0:
            return "Không có gì thay đổi"

        data.move_all_playable_players()

        return response

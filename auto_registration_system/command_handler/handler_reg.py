from auto_registration_system.data_structure.registration_data import RegistrationData
from auto_registration_system.exception.error_maker import ErrorMaker
from auto_registration_system.string_parser.string_parser import StringParser


class RegHandler:
    @staticmethod
    def handle(message: str, data: RegistrationData):
        try:
            slot_label = StringParser.get_last_word(message=message)
            current_message = StringParser.remove_last_word(message=message)
        except Exception as e:
            raise ErrorMaker.make_syntax_error_exception(message=message)

        players: list[str] = StringParser.split_names(current_message)
        for name in players:
            data.register_player(slot_label=slot_label, player=name)

        data.move_all_playable_players()

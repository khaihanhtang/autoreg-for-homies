import string

from auto_registration_system.data_structure.registration_data import RegistrationData
from auto_registration_system.exception.exception_last_word_not_found import LastWordNotFoundException
from auto_registration_system.string_parser.string_parser import StringParser


class RegHandler:
    @staticmethod
    def handle(message: string, data: RegistrationData):
        try:
            slot_label = StringParser.get_last_word(message=message)
            current_message = StringParser.remove_last_word(message=message)
        except:
            raise LastWordNotFoundException

        players: list[string] = StringParser.split_names(current_message)
        for name in players:
            data.insert_player(slot_label=slot_label, player=name)

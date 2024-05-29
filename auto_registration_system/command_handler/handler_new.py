import string

from auto_registration_system.data_structure.registration_data import RegistrationData
from auto_registration_system.string_parser.string_parser import StringParser
from ..exception.exception_number_as_int import NumberAsIntException
from ..exception.exeption_syntax_error import SyntaxErrorException

class NewHandler:

    @staticmethod
    def is_datevenue_line(message: string) -> bool:
        first_word: string = StringParser.get_first_word(message=message)
        if first_word == "[dv]":
            return True
        return False

    @staticmethod
    def handle(message: string, data: RegistrationData):
        current_datevenue = None
        for line in message.splitlines():
            if NewHandler.is_datevenue_line(message=message):
                current_datevenue = StringParser.remove_first_word(message=line)
                data.insert_datevenue(datevenue_name=current_datevenue)
            elif len(line.strip()) > 0:
                current_message = line.strip()
                max_num_players = 0
                try:
                    max_num_players = int(StringParser.get_last_word(message=current_message))
                    current_message = StringParser.remove_last_word(message=current_message)
                except:
                    raise NumberAsIntException
                if len(current_message) == 0:
                    raise SyntaxErrorException(message=line)
                data.insert_slot(datevenue_name=current_datevenue,slot_name=message,max_num_players=max_num_players)
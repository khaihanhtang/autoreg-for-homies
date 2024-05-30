from auto_registration_system.data_structure.registration_data import RegistrationData
from auto_registration_system.string_parser.string_parser import StringParser
from ..exception.exception_number_as_int import NumberAsIntException
from ..exception.error_maker import ErrorMaker
from ..exception.exception_slot_label_not_found import SlotLabelNotFoundException
from ..exception.exception_player_label_not_found import PlayerLabelNotFoundException
from ..exception.exception_datevenue_not_found import DateVenueNotFoundException
from ..term import Term


class NewHandler:

    @staticmethod
    def is_datevenue_line(message: str) -> bool:
        try:
            first_word: str = StringParser.get_first_word(message=message)
            if first_word == Term.DATE_VENUE:
                return True
        except Exception as e:
            return False

    @staticmethod
    def get_slot_label(message: str) -> str:
        first_word: str = StringParser.get_first_word(message=message)
        try:
            if not (first_word[0] == "[" and first_word[-1:] == "]" and len(first_word) >= 3):
                raise ErrorMaker.make_syntax_error_exception(message=message)
            return first_word[1:-1]
        except Exception as e:
            raise ErrorMaker.make_syntax_error_exception(message=message)

    @staticmethod
    def is_slot_line(message: str) -> bool:
        try:
            NewHandler.get_slot_label(message=message)
            return True
        except Exception as e:
            return False

    @staticmethod
    def get_player_label(message: str) -> str:
        first_word: str = StringParser.get_first_word(message=message)
        try:
            if not (first_word[-1:] == "." and len(first_word) >= 2):
                raise ErrorMaker.make_syntax_error_exception(message=message)
            return first_word[:-1]
        except Exception as e:
            raise ErrorMaker.make_syntax_error_exception(message=message)

    @staticmethod
    def is_player_line(message: str) -> bool:
        try:
            NewHandler.get_player_label(message=message)
            return True
        except Exception as e:
            return False

    @staticmethod
    def handle(message: str, data: RegistrationData):
        current_datevenue = None
        current_slot_label = None
        for line in message.splitlines():
            current_message = line.strip()
            if NewHandler.is_datevenue_line(message=line):
                current_datevenue = StringParser.remove_first_word(message=line)
                data.insert_datevenue(datevenue_name=current_datevenue)
            elif NewHandler.is_slot_line(message=line):
                current_slot_label: str = NewHandler.get_slot_label(message=current_message)
                current_message = StringParser.remove_first_word(message=current_message)

                max_num_players = 0
                try:
                    max_num_players = int(StringParser.get_last_word(message=current_message))
                    current_message = StringParser.remove_last_word(message=current_message)
                except Exception as e:
                    raise ErrorMaker.make_syntax_error_exception(message=line)

                try:
                    # if last word is the keyword '#players:'
                    if StringParser.get_last_word(current_message) == Term.NUM_PLAYERS:
                        current_message = StringParser.remove_last_word(current_message)

                    # remove if last character is ',' or '.'
                    if current_message[-1:] in {",", "."}:
                        current_message = StringParser.remove_redundant_spaces(current_message[:-1])
                except Exception as e:
                    pass

                # abort if empty string
                if len(current_message) == 0:
                    raise ErrorMaker.make_syntax_error_exception(message=line)

                if current_datevenue is None:
                    raise ErrorMaker.make_dv_not_found_exception(message=line)

                data.insert_slot(
                    datevenue=current_datevenue,
                    slot_label=current_slot_label,
                    slot_name=current_message,
                    max_num_players=max_num_players
                )
            elif NewHandler.is_player_line(message=line):
                current_message = line.strip()

                current_player_label: str = NewHandler.get_player_label(message=current_message)
                current_message = StringParser.remove_first_word(message=current_message)

                if current_datevenue is None:
                    raise ErrorMaker.make_dv_not_found_exception(message=line)
                if current_slot_label is None:
                    raise ErrorMaker.make_slot_not_found_exception(message=line)

                if len(current_message) > 0:
                    if current_player_label == Term.RESERVATION:
                        last_word: str = StringParser.get_last_word(message=current_message)
                        if last_word == Term.PLAYABLE:
                            current_message = StringParser.remove_last_word(message=current_message)
                            if len(current_message) > 0:
                                data.insert_reservation(
                                    slot_label=current_slot_label,
                                    player=current_message.title(),
                                    is_playable=True
                                )
                        else:
                            data.insert_reservation(
                                slot_label=current_slot_label,
                                player=current_message.title()
                            )
                    else:
                        data.insert_player(slot_label=current_slot_label,player=current_message.title())
            else:
                if len(current_message) > 0:
                    raise ErrorMaker.make_syntax_error_exception(message=line)
        data.move_all_playable_players()

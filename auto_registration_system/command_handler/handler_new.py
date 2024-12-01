from auto_registration_system.data_structure.registration_data import RegistrationData
from string_parser.string_parser import StringParser
from ..exception.error_maker import ErrorMaker
from ..term import Term


class NewHandler:

    @staticmethod
    def is_date_venue_line(message: str) -> bool:
        try:
            first_word: str = StringParser.get_first_word(message=message)
        except Exception:
            return False
        if first_word in {Term.DATE_VENUE, Term.DATE_VENUE_SHORTENED}:
            return True
        return False

    @staticmethod
    def get_slot_label(message: str) -> str:
        first_word: str = StringParser.get_first_word(message=message)
        tag = first_word
        if first_word[0] == "[" and first_word[-1:] == "]":
            if len(first_word) >= 3:
                tag = first_word[1:-1]
            else:
                tag = ""
        try:
            if not (tag.islower() and tag.isalnum()):
                raise ErrorMaker.make_syntax_error_exception(message=message)
            return tag
        except Exception:
            raise ErrorMaker.make_syntax_error_exception(message=message)

    @staticmethod
    def is_slot_line(message: str) -> bool:
        try:
            NewHandler.get_slot_label(message=message)
            return True
        except Exception:
            return False

    @staticmethod
    def get_player_label(message: str) -> str:
        first_word: str = StringParser.get_first_word(message=message)
        try:
            if not (first_word[-1:] == "." and len(first_word) >= 2):
                raise ErrorMaker.make_syntax_error_exception(message=message)
            return first_word[:-1]
        except Exception:
            raise ErrorMaker.make_syntax_error_exception(message=message)

    @staticmethod
    def is_player_line(message: str) -> bool:
        try:
            NewHandler.get_player_label(message=message)
            return True
        except Exception:
            return False

    @staticmethod
    def handle(message: str, data: RegistrationData, max_num_players: int) -> bool:
        message = StringParser.remove_command(message=message)
        current_date_venue: str or None = None
        current_slot_label: str or None = None
        count_processed: int = 0
        for line in message.splitlines():
            current_message = line.strip()
            count_processed += 1
            if NewHandler.is_date_venue_line(message=current_message):
                current_date_venue = StringParser.remove_first_word(message=current_message)
                data.insert_date_venue(date_venue=current_date_venue)
            elif NewHandler.is_slot_line(message=current_message):
                kept_message = current_message
                current_slot_label = NewHandler.get_slot_label(message=current_message)
                current_message = StringParser.remove_first_word(message=current_message)

                try:
                    num_players = int(StringParser.get_last_word(message=current_message))
                    current_message = StringParser.remove_last_word(message=current_message)
                except Exception:
                    raise ErrorMaker.make_syntax_error_exception(message=line)

                try:
                    # if last word is the keyword '#players:'
                    if StringParser.get_last_word(current_message) == Term.NUM_PLAYERS:
                        current_message = StringParser.remove_last_word(current_message)

                    # remove if last character is ',' or '.'
                    if current_message[-1:] in {",", "."}:
                        current_message = StringParser.remove_redundant_spaces(current_message[:-1])
                finally:
                    pass

                # abort if empty string
                if len(current_message) == 0:
                    raise ErrorMaker.make_syntax_error_exception(message=line)

                if current_date_venue is None:
                    raise ErrorMaker.make_dv_not_found_exception(message=line)

                if num_players > max_num_players:
                    raise ErrorMaker.make_num_players_exceeding_maximum_allowed_exception(
                        message=kept_message,
                        max_num_players=max_num_players
                    )

                data.insert_slot(
                    date_venue=current_date_venue,
                    slot_label=current_slot_label,
                    slot_name=current_message,
                    num_players=num_players
                )
            elif NewHandler.is_player_line(message=current_message):
                current_player_label: str = NewHandler.get_player_label(message=current_message)
                current_message = StringParser.remove_first_word(message=current_message)

                if current_date_venue is None:
                    raise ErrorMaker.make_dv_not_found_exception(message=line)
                if current_slot_label is None:
                    raise ErrorMaker.make_slot_not_found_exception(message=line)

                if len(current_message) > 0:
                    if current_player_label == Term.RESERVATION:
                        last_word: str = StringParser.get_last_word(message=current_message)
                        if last_word == Term.PENDING:
                            current_message = StringParser.remove_last_word(message=current_message)
                            if len(current_message) > 0:
                                data.reserve_player(
                                    slot_label=current_slot_label,
                                    player=current_message.title(),
                                    is_pending=True
                                )
                        else:
                            data.reserve_player(
                                slot_label=current_slot_label,
                                player=current_message.title()
                            )
                    else:
                        data.register_player(slot_label=current_slot_label, player=current_message.title())
            else:
                if len(current_message) > 0:
                    raise ErrorMaker.make_syntax_error_exception(message=line)
                count_processed -= 1
        if count_processed == 0:
            return False

        return True

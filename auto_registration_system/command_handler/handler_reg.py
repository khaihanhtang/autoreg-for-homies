from auto_registration_system.data_structure.registration_data import RegistrationData
from auto_registration_system.exception.error_maker import ErrorMaker
from auto_registration_system.exception.exception_name_conflict import NameConflictException
from string_parser.string_parser import StringParser


class RegHandler:
    @staticmethod
    def handle(message: str, data: RegistrationData) -> (str, list[str] or None, str):
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
        conflict_names: list[str] = list()
        for name in players:
            if len(name) > 0:
                count_processed += 1
                try:
                    StringParser.enforce_message_containing_alpha(message=name)
                    data.register_player(slot_label=slot_label, player=name)
                    response += f"{name} has been inserted into slot {slot_label}\n"
                except NameConflictException as e:
                    response += f"{repr(e)}\n"
                    conflict_names.append(name)
                except Exception as e:
                    response += f"{repr(e)}\n"
        if count_processed == 0:
            return "There is nothing changed!", None, slot_label

        if len(conflict_names) == 0:
            return response, None, slot_label
        return response, conflict_names, slot_label

    @staticmethod
    def make_suggestion(command_string: str, id_strings: list[str], slot_label: str) -> str or None:
        count = 0
        res: str = ""
        for name in id_strings:
            res += f"{count + 1}\\. `/{command_string} {
                StringParser.replace_escape_characters_for_markdown(message=name)
            } {slot_label}\n`"
            count += 1
        return f"If you want to deregister, you can hold to copy:\n{res}"

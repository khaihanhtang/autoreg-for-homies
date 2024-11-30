from auto_registration_system.exception.exception_name_conflict import NameConflictException
from auto_registration_system.exception.exception_syntax_error import SyntaxErrorException


class ErrorMaker:

    @staticmethod
    def make_syntax_error_exception(message: str) -> SyntaxErrorException:
        return SyntaxErrorException(message=message)

    @staticmethod
    def make_dv_not_found_exception(message: str) -> Exception:
        return Exception(f"Tag [dv] or dv not found at line '{message}'!")

    @staticmethod
    def make_slot_not_found_exception(message: str) -> Exception:
        return Exception(f"Slot '{message}' not found!")

    @staticmethod
    def make_dv_conflict_exception(message: str) -> Exception:
        return Exception(f"Date and time '{message}' are repeated!")

    @staticmethod
    def make_slot_conflict_exception(message: str) -> Exception:
        return Exception(f"Slot '{message}' is repeated!")

    @staticmethod
    def make_name_conflict_exception(message: str) -> NameConflictException:
        return NameConflictException(message)

    @staticmethod
    def make_name_not_found_exception(message: str) -> Exception:
        return Exception(f"Cannot find name '{message}'!")

    @staticmethod
    def make_admin_permission_error_exception() -> Exception:
        return Exception(f"This command requires admin permission!")

    @staticmethod
    def make_system_locked_exception() -> Exception:
        return Exception(f"The system is locked! Please wait until being unlock!")

    @staticmethod
    def make_chat_id_enforcement() -> Exception:
        return Exception(f"You cannot use bot here!")

    @staticmethod
    def make_pending_player_not_found_exception() -> Exception:
        return Exception(f"Cannot find pending player!")

    @staticmethod
    def make_single_line_not_satisfied_exception() -> Exception:
        return Exception(f"This command is only allowed in a single line!")

    @staticmethod
    def make_message_not_containing_alpha_exception(message: str) -> Exception:
        return Exception(f"'{message}' must contain at least an alphabet character (a - z)!")

    @staticmethod
    def make_message_containing_comma_exception(message: str) -> Exception:
        return Exception(f"'{message} is not valid because it contains ','!")

    @staticmethod
    def make_release_time_invalid_exception() -> Exception:
        return Exception(f"Release time must be after now!")

    @staticmethod
    def make_time_list_invalid_exception() -> Exception:
        return Exception(f"Time list must be strictly decreasing and has all positive integers!")

    @staticmethod
    def make_num_players_exceeding_maximum_allowed_exception(message: str, max_num_players: int) -> Exception:
        return Exception(f"At line '{message}', number of players exceeds {max_num_players}.")

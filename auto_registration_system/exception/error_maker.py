class ErrorMaker:

    @staticmethod
    def make_syntax_error_exception(message: str) -> Exception:
        return Exception(f"Potential syntax error at line '{message}'!")

    @staticmethod
    def make_dv_not_found_exception(message: str) -> Exception:
        return Exception(f"[dv] not found for '{message}'!")

    @staticmethod
    def make_slot_not_found_exception(message: str) -> Exception:
        return Exception(f"Slot not found for '{message}'!")

    @staticmethod
    def make_dv_conflict_exception(message: str) -> Exception:
        return Exception(f"[dv] conflict for '{message}'!")

    @staticmethod
    def make_slot_conflict_exception(message: str) -> Exception:
        return Exception(f"Slot conflict for '{message}'!")

    @staticmethod
    def make_name_conflict_exception(message: str) -> Exception:
        return Exception(f"Name conflict for '{message}'!")

    @staticmethod
    def make_name_not_found_exception(message: str) -> Exception:
        return Exception(f"Name not found for '{message}'!")

    @staticmethod
    def make_admin_permission_error_exception() -> Exception:
        return Exception(f"You are not admin to proceed this command!")

    @staticmethod
    def make_playable_player_not_found_exception() -> Exception:
        return Exception(f"Playable player not found for reservation!")
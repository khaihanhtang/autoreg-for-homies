class ErrorMaker:

    @staticmethod
    def make_syntax_error_exception(message: str) -> Exception:
        return Exception(f"Có thể sai cú pháp tại '{message}'!")

    @staticmethod
    def make_dv_not_found_exception(message: str) -> Exception:
        return Exception(f"Không tìm thấy tag [dv] hoặc dv ở dòng '{message}'!")

    @staticmethod
    def make_slot_not_found_exception(message: str) -> Exception:
        return Exception(f"Không tìm thấy slot '{message}'!")

    @staticmethod
    def make_dv_conflict_exception(message: str) -> Exception:
        return Exception(f"Xung đột ngày và địa điểm '{message}'!")

    @staticmethod
    def make_slot_conflict_exception(message: str) -> Exception:
        return Exception(f"Xung đột slot '{message}'!")

    @staticmethod
    def make_name_conflict_exception(message: str) -> Exception:
        return Exception(f"Xung đột tên '{message}'!")

    @staticmethod
    def make_name_not_found_exception(message: str) -> Exception:
        return Exception(f"Không tìm thấy tên '{message}'!")

    @staticmethod
    def make_admin_permission_error_exception() -> Exception:
        return Exception(f"Lệnh này cần quyền admin!")

    @staticmethod
    def make_chat_id_enforcement() -> Exception:
        return Exception(f"Bạn không thể sử dụng bot ở đây!")

    @staticmethod
    def make_playable_player_not_found_exception() -> Exception:
        return Exception(f"Không tìm thấy người chơi để dự bị!")

    @staticmethod
    def make_single_line_not_satisfied_exception() -> Exception:
        return Exception(f"Lệnh này chỉ được phép trên 1 dòng!")

    @staticmethod
    def make_message_not_containing_alpha_exception(message: str) -> Exception:
        return Exception(f"'{message}' phải tồn tại ít nhất một chữ cái!")
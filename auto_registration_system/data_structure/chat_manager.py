from auto_registration_system.exception.error_maker import ErrorMaker


class ChatManager:

    @staticmethod
    def is_chat_id_allowed(chat_id: int, allowed_chat_ids: set[int]) -> bool:
        return chat_id in allowed_chat_ids

    @staticmethod
    def enforce_chat_id(chat_id: int, allowed_chat_ids: set[int]):
        if not ChatManager.is_chat_id_allowed(chat_id=chat_id, allowed_chat_ids=allowed_chat_ids):
            raise ErrorMaker.make_chat_id_enforcement()

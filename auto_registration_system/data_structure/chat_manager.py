from auto_registration_system.exception.error_maker import ErrorMaker


class ChatManager:

    def __init__(self, chat_ids: set[int]):
        self._chat_ids = chat_ids

    def enforce_chat_id(self, chat_id: int):
        if chat_id not in self._chat_ids:
            raise ErrorMaker.make_chat_id_enforcement()

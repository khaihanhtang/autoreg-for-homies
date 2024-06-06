from auto_registration_system.exception.error_maker import ErrorMaker


class ChatManager:

    def __init__(self, chat_id: int):
        self._chat_id = chat_id

    def enforce_chat_id(self, chat_id: int):
        if chat_id != self._chat_id:
            raise ErrorMaker.make_chat_id_enforcement()
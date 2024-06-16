class NameConflictException(Exception):

    def __init__(self, message):
        self._message: str = message

    def __repr__(self) -> str:
        return f"{self._message} đã được đăng kí trước đó!"

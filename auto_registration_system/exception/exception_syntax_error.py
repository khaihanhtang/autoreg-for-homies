class SyntaxErrorException(Exception):

    def __init__(self, message, hint: str = ""):
        self._message: str = message
        self._hint: str = hint

    def __repr__(self) -> str:
        return f"Có thể sai cú pháp tại '{self._message}'! - {self._hint}"

class SyntaxErrorException(Exception):

    def __init__(self, message):
        self._message: str = message

    def __repr__(self) -> str:
        return f"Có thể sai cú pháp tại '{self._message}'!"

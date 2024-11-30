class Reservation:

    def __init__(self, name: str, is_pending: bool):
        self._name: str = name
        self._is_pending: bool = is_pending

    @property
    def name(self) -> str:
        return self._name

    @property
    def is_pending(self) -> bool:
        return self._is_pending

    @is_pending.setter
    def is_pending(self, is_pending: bool):
        self._is_pending = is_pending

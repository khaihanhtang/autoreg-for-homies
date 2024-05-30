class Reservation:

    def __init__(self, name: str, is_playable: bool):
        self._name = name
        self._is_playable = is_playable

    @property
    def name(self) -> str:
        return self._name

    @property
    def is_playable(self) -> bool:
        return self._is_playable

    @is_playable.setter
    def is_playable(self, is_playable: bool):
        self._is_playable = is_playable

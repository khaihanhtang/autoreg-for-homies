from auto_registration_system.exception.error_maker import ErrorMaker


class LockManager:

    def __init__(self, locked: bool):
        self._locked = locked

    @property
    def locked(self) -> bool:
        return self._locked

    @locked.setter
    def locked(self, new_locked_value: bool):
        self._locked = new_locked_value

    def enforce_system_unlocked(self):
        if self._locked:
            raise ErrorMaker.make_system_locked_exception()
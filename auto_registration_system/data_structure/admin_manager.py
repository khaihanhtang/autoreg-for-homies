from ..exception.error_maker import ErrorMaker


class AdminManager:

    def __init__(self, admins: set[str]):
        self._admins = admins

    @property
    def admins(self) -> set[str]:
        return self._admins

    def is_admin(self, username: str) -> bool:
        if username in self._admins or username == "*":
            return True
        return False

    def enforce_admin(self, username: str):
        if not self.is_admin(username=username):
            raise ErrorMaker.make_admin_permission_error_exception()

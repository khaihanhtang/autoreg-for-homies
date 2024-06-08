from ..exception.error_maker import ErrorMaker


class AdminManager:

    def __init__(self, admin_list: set[str]):
        self._admin_list = admin_list

    @property
    def admin_list(self) -> set[str]:
        return self._admin_list

    def is_admin(self, username: str) -> bool:
        if username in self._admin_list:
            return True
        return False

    def enforce_admin(self, username: str):
        if not self.is_admin(username=username):
            raise ErrorMaker.make_admin_permission_error_exception()

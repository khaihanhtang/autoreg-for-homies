from ..exception.error_maker import ErrorMaker


class AdminManager:

    def __init__(self, admin_list: set[str]):
        self._admin_list = admin_list

    @property
    def admin_list(self) -> set[str]:
        return self._admin_list

    def enforce_admin(self, username: str):
        if username not in self._admin_list:
            raise ErrorMaker.make_admin_permission_error_exception()

from ..exception.error_maker import ErrorMaker


class AdminManager:
    admin_list: set = {"khaihanhtang", "trung1973", "bibi_tran"}

    @staticmethod
    def enforce_admin(username: str):
        if username not in AdminManager.admin_list:
            raise ErrorMaker.make_admin_permission_error_exception()

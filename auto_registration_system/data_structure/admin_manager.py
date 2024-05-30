from ..exception.error_maker import ErrorMaker
from ..exception.exception_admin_requirement import AdminRequirementException


class AdminManager:
    admin_list: set = {"khaihanhtang"}

    def enforce_admin(username: str):
        if username not in AdminManager.admin_list:
            raise ErrorMaker.make_admin_permission_error_exception()

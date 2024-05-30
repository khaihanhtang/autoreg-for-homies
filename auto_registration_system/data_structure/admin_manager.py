from ..exception.exception_admin_requirement import AdminRequirementException


class AdminManager:
    admin_list: set = {"khaihanhtang"}

    def enforce_admin(username: str):
        if username not in AdminManager.admin_list:
            raise AdminRequirementException

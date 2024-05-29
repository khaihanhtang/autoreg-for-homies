import string


class Admin:
    admin_list: set = {"khaihanhtang"}

    def is_admin(username: string) -> bool:
        if username in Admin.admin_list:
            return True
        return False
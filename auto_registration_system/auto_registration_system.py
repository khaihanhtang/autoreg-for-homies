import string
from data_structure.registration_data import RegistrationData
from data_structure.admin_manager import AdminManager
from command_handler.handler_new import NewHandler

class AutoRegistrationSystem:

    def __init__(self):
        self.data: RegistrationData = None

    def handle_new(self, username: string, message: string) -> string:
        try:
            AdminManager.enforce_admin(username=username)
        except Exception as e:
            return e.message
        self.data = AutoRegistrationSystem()

        try:
            NewHandler.handle(message=message, data=self.data)
        except Exception as e:
            return e.message
        
from telegram import MessageEntity

from auto_registration_system.exception.error_maker import ErrorMaker


class AkaSemanticParser:

    @staticmethod
    def split_components(username: str, message: str, message_entities: dict[MessageEntity, str]):
        if len(message_entities) == 0:
            pass    # case user
        elif len(message_entities) == 1:
            pass    # case admin
        else:
            raise ErrorMaker.make_syntax_error_exception(message=message)

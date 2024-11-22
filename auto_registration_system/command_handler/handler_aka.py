from telegram import MessageEntity

from auto_registration_system.data_structure.identity_manager import IdentityManager
from auto_registration_system.exception.error_maker import ErrorMaker
from string_parser.string_parser import StringParser


class AkaHandler:

    @staticmethod
    def _parse_admin_case(message: str, command_string: str, message_entity: MessageEntity) \
            -> (int, str, str):    # id, full_name, alias
        if not message[len(command_string) + 1:message_entity.offset].isspace():
            raise ErrorMaker.make_syntax_error_exception(message=message)
        raw_alias: str = message[message_entity.offset + message_entity.length:]
        if ',' in raw_alias:
            raise ErrorMaker.make_message_containing_comma_exception(message=message)
        res_id = message_entity.user.id
        res_full_name = StringParser.process_telegram_full_name(message_entity.user.full_name)
        res_alias = StringParser.split_names(message=raw_alias)[0]
        return res_id, res_full_name, res_alias

    @staticmethod
    def _parse_user_case(sender_id: int, sender_full_name: str, message: str) \
            -> (int, str, str):  # id, full_name, alias
        raw_alias: str = StringParser.remove_command(message=message)
        if ',' in raw_alias:
            raise ErrorMaker.make_message_containing_comma_exception(message=message)
        return sender_id, sender_full_name, StringParser.split_names(message=raw_alias)[0]

    @staticmethod
    def handle(sender_id: int, sender_full_name: str, message: str,
               message_entities: dict[MessageEntity, str], identity_manager: IdentityManager) -> str:
        if len(message_entities) >= 1:
            # message_entity = list(message_entities.keys())[0]
            # affected_id, affected_name, affected_alias = AkaHandler._parse_admin_case(
            #     message=message,
            #     command_string=command_string,
            #     message_entity=message_entity
            # )
            raise ErrorMaker.make_syntax_error_exception(message=message)  # this functionality is skipped
        else:
            affected_id, affected_name, affected_alias = AkaHandler._parse_user_case(
                sender_id=sender_id,
                sender_full_name=sender_full_name,
                message=message
            )
        if affected_alias == "":
            alias = identity_manager.get_alias(telegram_id=affected_id)
            if alias is None:
                return f"Bạn chưa có alias!"
            return f"Alias của bạn là '{alias}'"
        # else:
        identity_manager.set_alias(affected_id, affected_alias)
        return f"Alias mới của bạn là '{affected_alias}'"

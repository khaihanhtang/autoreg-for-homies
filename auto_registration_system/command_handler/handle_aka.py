from telegram import MessageEntity

from auto_registration_system.data_structure.identity_manager import IdentityManager
from auto_registration_system.exception.error_maker import ErrorMaker
from string_parser.string_parser import StringParser


class AkaHandler:

    @staticmethod
    def _parse_admin_case(message: str, command_string: str, message_entity: MessageEntity) \
            -> (int, str, str):    # id, full_name, alias
        try:
            if not message[len(command_string) + 1:message_entity.offset].isspace():
                raise ErrorMaker.make_syntax_error_exception(message=message)
            raw_alias: str = message[message_entity.offset + message_entity.length:]
            print(raw_alias)
            if ',' in raw_alias:
                raise ErrorMaker.make_message_containing_comma_exception(message=message)
            res_id = message_entity.user.id
            res_full_name = StringParser.process_telegram_full_name(message_entity.user.full_name)
            res_alias = StringParser.split_names(message=raw_alias)[0]
            print(res_id, res_full_name, res_alias)
            return res_id, res_full_name, res_alias
        except Exception:
            pass

    @staticmethod
    def _parse_user_case(sender_id: int, sender_full_name: str, message: str, command_string: str) \
            -> (int, str, str):  # id, full_name, alias
        try:
            raw_alias: str = message[len(command_string) + 1:]
            if ',' in raw_alias:
                raise ErrorMaker.make_message_containing_comma_exception(message=message)
            return sender_id, sender_full_name, StringParser.split_names(message=raw_alias)[0]
        except Exception:
            pass

    @staticmethod
    def handle(sender_id: int, sender_full_name: str, message: str, command_string: str,
               message_entities: dict[MessageEntity, str], identity_manager: IdentityManager) -> (int, str):
        if len(message_entities) == 1:
            message_entity = list(message_entities.keys())[0]
            print(message, command_string)
            print(message_entity)
            affected_id, affected_name, affected_alias = AkaHandler._parse_admin_case(
                message=message,
                command_string=command_string,
                message_entity=message_entity
            )
        else:
            affected_id, affected_name, affected_alias = AkaHandler._parse_user_case(
                sender_id=sender_id,
                sender_full_name=sender_full_name,
                message=message,
                command_string=command_string
            )
        identity_manager.set_alias(affected_id, affected_alias)
        return affected_id, affected_name, affected_alias

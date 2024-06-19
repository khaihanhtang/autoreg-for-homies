import re

from auto_registration_system.exception.error_maker import ErrorMaker
from auto_registration_system.exception.exception_last_word_not_found import LastWordNotFoundException
from auto_registration_system.exception.exception_first_word_not_found import FirstWordNotFoundException


class StringParser:

    @staticmethod
    def remove_redundant_spaces(message: str) -> str:
        return re.sub(' +', ' ', message).strip()

    @staticmethod
    def remove_first_word(message: str) -> str:
        res: str = message.strip()
        if len(res) == 0:
            raise FirstWordNotFoundException
        return StringParser.remove_redundant_spaces(res.partition(' ')[2].strip())

    @staticmethod
    def remove_command(message: str) -> str:
        current_message: str = message.strip()
        if len(current_message) == 0:
            return current_message
        res: str = ""
        split_lines = current_message.splitlines()
        for i, line in enumerate(split_lines):
            if i == 0 and line[0] == '/':
                res += StringParser.remove_redundant_spaces(line.partition(' ')[2])
            else:
                res += line
            if i + 1 < len(split_lines):
                res += "\n"
        return res

    @staticmethod
    def get_first_word(message: str) -> str:
        try:
            return message.split()[0]
        except Exception:
            raise FirstWordNotFoundException

    @staticmethod
    def get_last_word(message: str) -> str:
        try:
            return message.split()[-1]
        except Exception:
            raise LastWordNotFoundException

    @staticmethod
    def remove_last_word(message: str) -> str:
        res: str = message.strip()

        if len(res) == 0:
            raise LastWordNotFoundException

        split_res = res.rsplit(' ', 1)

        # this string has exactly one word
        if len(split_res) == 1:
            return ""
        return StringParser.remove_redundant_spaces(split_res[0])

    @staticmethod
    def split_names(message: str) -> list[str]:
        res: list[str] = message.split(',')
        for i, name in enumerate(res):
            res[i] = StringParser.remove_redundant_spaces(name).title()
        return res

    @staticmethod
    def enforce_message_containing_alpha(message: str):
        containing_alpha: bool = False
        for character in list(message):
            if character.isalpha():
                containing_alpha = True
        if not containing_alpha:
            raise ErrorMaker.make_message_not_containing_alpha_exception(message=message)

    @staticmethod
    def enforce_single_line_message(message: str):
        if '\n' in message:
            raise ErrorMaker.make_single_line_not_satisfied_exception()

    @staticmethod
    def process_telegram_full_name(telegram_full_name: str) -> str:
        char_list = list(telegram_full_name)
        for i, c in enumerate(char_list):
            if c == ",":
                char_list[i] = ""
        full_name = StringParser.split_names(message="".join(char_list))[0]
        return full_name

    @staticmethod
    def replace_escape_characters_for_markdown(message: str) -> str:
        return (message.replace("_", '\\_')
                .replace('*', '\\*')
                .replace('[', '\\[')
                .replace(']', '\\]')
                .replace('(', '\\(')
                .replace(')', '\\)')
                .replace('~', '\\~')
                .replace('`', '\\`')
                .replace('>', '\\>')
                .replace('#', '\\#')
                .replace('+', '\\+')
                .replace('+', '\\+')
                .replace('-', '\\-')
                .replace('=', '\\=')
                .replace('|', '\\|')
                .replace('{', '\\{')
                .replace('}', '\\}')
                .replace('.', '\\.')
                .replace('!', '\\!')
                )

    @staticmethod
    def make_clickable_link_for_telegram_id(telegram_id: int, full_name: str) -> str:
        return f"[{StringParser.replace_escape_characters_for_markdown(full_name)}](tg://user?id={telegram_id})"

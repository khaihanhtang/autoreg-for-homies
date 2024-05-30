import re

from ..exception.error_maker import ErrorMaker
from ..exception.exception_last_word_not_found import LastWordNotFoundException
from ..exception.exception_first_word_not_found import FirstWordNotFoundException


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
        except Exception as e:
            raise FirstWordNotFoundException

    @staticmethod
    def get_last_word(message: str) -> str:
        try:
            return message.split()[-1]
        except Exception as e:
            raise LastWordNotFoundException

    @staticmethod
    def remove_last_word(message: str) -> str:
        res: str = message.strip()
        if len(res) == 0:
            raise LastWordNotFoundException
        return StringParser.remove_redundant_spaces(res.rsplit(' ', 1)[0])

    @staticmethod
    def split_names(message: str) -> list[str]:
        res: list[str] = message.split(',')
        for i, name in enumerate(res):
            res[i] = StringParser.remove_redundant_spaces(name).title()
        return res

    @staticmethod
    def enforce_single_line_message(message: str):
        if '\n' in message:
            raise ErrorMaker.make_single_line_not_satisfied_exception()
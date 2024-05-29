import string
import re
from typing import List

from ..exception.exception_last_word_not_found import LastWordNotFoundException
from ..exception.exception_first_word_not_found import FirstWordNotFoundException
from ..exception.exception_slot_label_not_found import SlotLabelNotFoundException

class StringParser:

    @staticmethod
    def remove_redundant_spaces(message: string) -> string:
        return re.sub(' +', ' ', message).strip()

    @staticmethod
    def remove_first_word(message: string) -> string:
        res: string = message.strip()
        if len(res) == 0:
            raise FirstWordNotFoundException
        return StringParser.remove_redundant_spaces(res.partition(' ')[2].strip())

    @staticmethod
    def remove_command(message: string) -> string:
        current_message: string = message.strip()
        if len(current_message) == 0:
            return current_message
        res: string = ""
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
    def get_first_word(message: string) -> string:
        try:
            return message.split()[0]
        except Exception as e:
            raise FirstWordNotFoundException

    @staticmethod
    def get_last_word(message: string) -> string:
        try:
            return message.split()[-1]
        except Exception as e:
            raise LastWordNotFoundException

    @staticmethod
    def remove_last_word(message: string) -> string:
        res: string = message.strip()
        if len(res) == 0:
            raise LastWordNotFoundException
        return StringParser.remove_redundant_spaces(res.rsplit(' ', 1)[0])

    @staticmethod
    def split_names(message: string) -> List[string]:
        res: List[string] = message.split(',')
        for i, name in enumerate(res):
            res[i] = StringParser.remove_redundant_spaces(name).title()
        return res
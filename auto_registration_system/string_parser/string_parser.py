import string
import re
from typing import List

from ..exception.exception_last_word_not_found import LastWordNotFoundException
from ..exception.exception_first_word_not_found import FirstWordNotFoundException

class StringParser:

    @staticmethod
    def remove_first_word(message: string) -> string:
        res: string = message.strip()
        if len(res) == 0:
            raise FirstWordNotFoundException
        return res.partition(' ')[2].strip()

    @staticmethod
    def remove_command(message: string) -> string:
        res: string = message.strip()
        if len(res) == 0:
            return res
        if res[0] == '/':
            res = res.partition(' ')[2].strip()
        return res

    @staticmethod
    def get_first_word(message: string) -> string:
        try:
            return message.split()[0]
        except:
            raise FirstWordNotFoundException
    @staticmethod
    def get_last_word(message: string) -> string:
        try:
            return message.split()[-1]
        except:
            raise LastWordNotFoundException

    @staticmethod
    def remove_last_word(message: string) -> string:
        res: string = message.strip()
        if len(res) == 0:
            raise LastWordNotFoundException
        return res.rsplit(' ', 1)[0]

    @staticmethod
    def split_names(message: string) -> List[string]:
        res: List[string] = message.split(',')
        for i, name in enumerate(res):
            res[i] = re.sub(' +', ' ', name).strip().title()
        return res
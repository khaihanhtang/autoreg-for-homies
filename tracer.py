import logging
from typing import BinaryIO

from auto_registration_system.data_structure.time_manager import TimeManager


class Tracer:

    def __init__(self, file_name_log: str, file_name_history: str, time_manager: TimeManager):
        self._file_name_log = file_name_log
        logging.basicConfig(filename=self._file_name_log, encoding='utf-8', level=logging.INFO)
        self._file_name_history = file_name_history
        self._time_manager = time_manager

    def log(self, message: str, is_history_required: bool = True):
        logging.info(msg=f"{message}")
        if is_history_required:
            with open(file=self._file_name_history, mode="a", encoding="utf-8") as f:
                f.write(f"## {self._time_manager.now_to_str()}\n")
                f.write(f"{message}\n\n")

    def load_file_history(self) -> BinaryIO:
        return open(self._file_name_history, 'rb')

import logging

from time_manager import TimeManager


class Tracer:

    def __init__(self, log_file_name: str, history_file_name: str, time_manager: TimeManager):
        self._log_file_name = log_file_name
        self._history_file_name = history_file_name
        self._time_manager = time_manager

    def log(self, message: str):
        logging.info(msg=f"{message}")
        with open(file=self._history_file_name, mode="a", encoding="utf-8") as f:
            f.write(f"## {self._time_manager.now_to_str()}\n")
            f.write(f"{message}\n\n")

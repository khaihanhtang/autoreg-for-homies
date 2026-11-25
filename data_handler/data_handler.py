import json
import os

from auto_registration_system.data_structure.identity_manager import IdentityManager
from auto_registration_system.data_structure.time_manager import TimeManager
from tracer import Tracer


class DataHandler:

    def __init__(self, directory_data: str,
                 file_name_log: str, file_name_history: str, file_name_alias: str, file_name_deletion_queue: str,
                 file_name_main_list: str, file_name_release_time: str, file_name_pre_released_list: str,
                 file_name_state: str = "state.json"):
        if not os.path.isdir(directory_data):
            os.makedirs(directory_data)
        self._full_file_name_log: str = DataHandler.make_full_file_name(
            directory_data=directory_data,
            file_name=file_name_log
        )
        self._full_file_name_history: str = DataHandler.make_full_file_name(
            directory_data=directory_data,
            file_name=file_name_history
        )
        self._full_file_name_alias: str = DataHandler.make_full_file_name(
            directory_data=directory_data,
            file_name=file_name_alias
        )
        self._full_file_name_deletion_queue: str = DataHandler.make_full_file_name(
            directory_data=directory_data,
            file_name=file_name_deletion_queue
        )
        self._full_file_name_main_list: str = DataHandler.make_full_file_name(
            directory_data=directory_data,
            file_name=file_name_main_list
        )
        self._full_file_name_release_time: str = DataHandler.make_full_file_name(
            directory_data=directory_data,
            file_name=file_name_release_time
        )
        self._full_file_name_pre_released_list: str = DataHandler.make_full_file_name(
            directory_data=directory_data,
            file_name=file_name_pre_released_list
        )
        self._full_file_name_state = DataHandler.make_full_file_name(directory_data, file_name_state)

    @staticmethod
    def make_full_file_name(directory_data: str, file_name: str) -> str:
        return directory_data + "/" + file_name

    def write_state(self, state: dict) -> None:
        temporary_state_file = self._full_file_name_state + ".tmp"
        with open(temporary_state_file, "w", encoding="utf-8") as file:
            json.dump(state, file, ensure_ascii=False)
            file.flush()
            os.fsync(file.fileno())
        os.replace(temporary_state_file, self._full_file_name_state)

    def read_state(self) -> dict | None:
        try:
            with open(self._full_file_name_state, encoding="utf-8") as file:
                state = json.load(file)
        except FileNotFoundError:
            return None
        if not isinstance(state, dict):
            raise ValueError(f"Invalid saved state in {self._full_file_name_state}")
        return state

    @staticmethod
    def _read_legacy_text(file_name: str) -> str | None:
        try:
            with open(file_name, encoding="utf-8") as file:
                return file.read()
        except FileNotFoundError:
            return None

    def read_legacy_state(self) -> tuple[str | None, str | None, str | None]:
        return (
            self._read_legacy_text(self._full_file_name_main_list),
            self._read_legacy_text(self._full_file_name_release_time),
            self._read_legacy_text(self._full_file_name_pre_released_list),
        )

    def load_identity_manager(self) -> IdentityManager:
        return IdentityManager(file_name_alias=self._full_file_name_alias)

    def load_tracer(self, time_manager: TimeManager) -> Tracer:
        return Tracer(
            file_name_log=self._full_file_name_log,
            file_name_history=self._full_file_name_history,
            time_manager=time_manager
        )

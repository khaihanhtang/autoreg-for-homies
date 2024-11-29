import os

from auto_registration_system.data_structure.identity_manager import IdentityManager
from auto_registration_system.data_structure.time_manager import TimeManager
from tracer import Tracer


class DataHandler:

    def __init__(self, directory_data: str,
                 file_name_log: str, file_name_history: str, file_name_alias: str, file_name_deletion_queue: str,
                 file_name_main_list: str, file_name_release_time: str, file_name_pre_released_list: str):
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

    @staticmethod
    def make_full_file_name(directory_data: str, file_name: str) -> str:
        return directory_data + "/" + file_name

    def write_data_to_files(self, main_list_as_str: str, release_time_as_str: str, pre_released_list_as_str: str):
        with open(file=self._full_file_name_main_list, mode="w", encoding="utf-8") as text_file:
            if main_list_as_str is not None:
                text_file.write(main_list_as_str)
            else:
                text_file.write("")
        with open(file=self._full_file_name_release_time, mode="w", encoding="utf-8") as text_file:
            if release_time_as_str is not None:
                text_file.write(release_time_as_str)
            else:
                text_file.write("")
        with open(file=self._full_file_name_pre_released_list, mode="w", encoding="utf-8") as text_file:
            if pre_released_list_as_str is not None:
                text_file.write(pre_released_list_as_str)
            else:
                text_file.write("")

    def read_data_from_files(self) -> (str, str, str):
        main_list_as_str: str | None = None
        release_time_as_str: str | None = None
        pre_released_list_as_str: str | None = None
        try:
            with open(file=self._full_file_name_main_list, mode="r", encoding="utf-8") as text_file:
                main_list_as_str: str = text_file.read()
        except Exception:
            print(f"File {self._full_file_name_main_list} may not exist or error!")

        try:
            with open(file=self._full_file_name_release_time, mode="r", encoding="utf-8") as text_file:
                release_time_as_str: str = text_file.read()
        except Exception:
            print(f"File {self._full_file_name_release_time} may not exist or error!")

        try:
            with open(file=self._full_file_name_pre_released_list, mode="r", encoding="utf-8") as text_file:
                pre_released_list_as_str: str = text_file.read()
        except Exception:
            print(f"File {self._full_file_name_pre_released_list} may not exist or error!")
        return main_list_as_str, release_time_as_str, pre_released_list_as_str

    def load_identity_manager(self) -> IdentityManager:
        return IdentityManager(file_name_alias=self._full_file_name_alias)

    def load_tracer(self, time_manager: TimeManager) -> Tracer:
        return Tracer(
            file_name_log=self._full_file_name_log,
            file_name_history=self._full_file_name_history,
            time_manager=time_manager
        )

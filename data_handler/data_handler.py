import os


class DataHandler:

    def __init__(self, directory_data: str, file_main_list: str, file_release_time: str, file_pre_released_list: str):
        if not os.path.isdir(directory_data):
            os.makedirs(directory_data)
        self._file_main_list: str = DataHandler.make_full_file_name(
            directory_data=directory_data,
            file_name=file_main_list
        )
        self._file_release_time: str = DataHandler.make_full_file_name(
            directory_data=directory_data,
            file_name=file_release_time
        )
        self._file_pre_released_list: str = DataHandler.make_full_file_name(
            directory_data=directory_data,
            file_name=file_pre_released_list
        )

    @staticmethod
    def make_full_file_name(directory_data: str, file_name: str) -> str:
        return directory_data + "/" + file_name

    def write_data_to_files(self, main_list_as_str: str, release_time_as_str: str, pre_released_list_as_str: str):
        with open(file=self._file_main_list, mode="w", encoding="utf-8") as text_file:
            if main_list_as_str is not None:
                text_file.write(main_list_as_str)
            else:
                text_file.write("")
        with open(file=self._file_release_time, mode="w", encoding="utf-8") as text_file:
            if release_time_as_str is not None:
                text_file.write(release_time_as_str)
            else:
                text_file.write("")
        with open(file=self._file_pre_released_list, mode="w", encoding="utf-8") as text_file:
            if pre_released_list_as_str is not None:
                text_file.write(pre_released_list_as_str)
            else:
                text_file.write("")

    def read_data_from_files(self) -> (str, str, str):
        main_list_as_str: str or None = None
        release_time_as_str: str or None = None
        pre_released_list_as_str: str or None = None
        try:
            with open(file=self._file_main_list, mode="r", encoding="utf-8") as text_file:
                main_list_as_str: str = text_file.read()
        except Exception:
            print(f"File {self._file_main_list} may not exist or error!")

        try:
            with open(file=self._file_release_time, mode="r", encoding="utf-8") as text_file:
                release_time_as_str: str = text_file.read()
        except Exception:
            print(f"File {self._file_release_time} may not exist or error!")

        try:
            with open(file=self._file_pre_released_list, mode="r", encoding="utf-8") as text_file:
                pre_released_list_as_str: str = text_file.read()
        except Exception:
            print(f"File {self._file_pre_released_list} may not exist or error!")
        return main_list_as_str, release_time_as_str, pre_released_list_as_str

import pytz
from pytz.tzinfo import StaticTzInfo


class Config:
    admins: set[str] = {"khaihanhtang", "trung1973", "bibi_tran", "ledung_jenny", "thanhdatkma"}
    allowed_chat_ids: set[int] = {-1002228202437, -4273658267}  # official
    default_chat_id = -1002228202437  # official
    # allowed_chat_ids: set[int] = {-4273658267}  # test
    # default_chat_id = -4273658267  # test
    log_file_name: str = "activities.log"
    history_file_name: str = "history.txt"
    alias_file_name: str = "alias.json"
    time_zone: StaticTzInfo = pytz.timezone("Asia/Singapore")
    input_time_format: str = "%H:%M:%S %d/%m/%Y"
    output_time_format: str = "%H:%M:%S %d-%B-%Y (%Z)"

    # variables for release time
    job_name_for_release: str = "release"  # used when creating job for the telegram bot to run before release
    repeating_interval_for_release: float = 3  # number of seconds after every 2 consecutive repeats
    reminder_time_list: list[int] = [60, 5, 1]

    # variable for data storage
    directory_data: str = "data"
    file_name_main_list: str = "main_list.txt"
    file_name_release_time: str = "release_time.txt"
    file_name_pre_released_list: str = "pre_released_list.txt"
    
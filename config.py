import pytz
from pytz.tzinfo import StaticTzInfo


class Config:
    # Admin rights use Telegram usernames. Allowed chat IDs govern public registration,
    # and the default chat receives scheduled releases and announcements.
    admins: set[str] = {"khaihanhtang", "bibi_tran", "ledung_jenny"}
    allowed_chat_ids: set[int] = {-1002228202437, -4273658267}  # official
    default_chat_id = -1002228202437  # official
    # allowed_chat_ids: set[int] = {-4273658267}  # test
    # default_chat_id = -4273658267  # test
    time_zone: StaticTzInfo = pytz.timezone("Asia/Singapore")
    input_time_format: str = "%H:%M:%S %d/%m/%Y"
    output_time_format: str = "%H:%M:%S %A %d-%B-%Y (%Z)"

    # variables for setting the list of players
    max_num_players_per_slot = 50

    # The timer uses local dates and these lead times in minutes. Put the longest reminder first.
    job_name_for_release: str = "release"  # used when creating job for the telegram bot to run before release
    reminder_time_list: list[int] = [5]  # this is the list of numbers of minutes
    pre_release_reset_minutes: int = 30  # Minutes before release to clear the active list and unlock. Set 0 to disable.

    # variables for deleting messages
    job_name_for_deleting: str = "delete"  # used when creating job for the telegram bot to run before deleting messages
    repeating_interval_for_deleting: int = 15  # this is the number of seconds before deleting message

    # variable for data storage
    directory_data: str = "data"
    file_name_log: str = "activities.log"
    file_name_history: str = "history.txt"
    file_name_alias: str = "alias.json"
    file_name_deletion_queue: str = "deletion_queue.json"
    # The text files support legacy startup. The JSON snapshot is the current state file.
    file_name_main_list: str = "main_list.txt"
    file_name_release_time: str = "release_time.txt"
    file_name_pre_released_list: str = "pre_released_list.txt"
    file_name_state: str = "state.json"

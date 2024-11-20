import pytz
from pytz.tzinfo import StaticTzInfo


class Config:
    admins: set[str] = {"khaihanhtang", "trung1973", "bibi_tran", "ledung_jenny", "thanhdatkma"}
    # chat_ids: set[int] = {-1002228202437, -4273658267}  # official
    chat_ids: set[int] = {-4273658267}  # test
    log_file_name: str = "activities.log"
    history_file_name: str = "history.md"
    alias_file_name: str = "alias.json"
    time_zone: StaticTzInfo = pytz.timezone("Asia/Singapore")
    input_time_format: str = "%H:%M:%S %d/%m/%Y"
    output_time_format: str = "%H:%M:%S %d-%B-%Y (%Z)"

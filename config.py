import pytz
from pytz.tzinfo import StaticTzInfo


class Config:
    admins: set[str] = {"khaihanhtang", "trung1973", "bibi_tran", "ledung_jenny", "thanhdatkma"}
    chat_ids: set[int] = {-1002228202437, -4273658267}
    log_file_name: str = "activities.log"
    history_file_name: str = "history.md"
    time_zone: StaticTzInfo = pytz.timezone("Asia/Singapore")
    time_format: str = "%H:%M:%S %d/%m/%Y"
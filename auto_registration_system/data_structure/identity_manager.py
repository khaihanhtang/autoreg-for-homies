import json


class IdentityManager:

    def __init__(self, file_name_alias):
        self._file_name_alias = file_name_alias
        self._id_to_alias: dict[int, str] = IdentityManager._load(alias_file_name=self._file_name_alias)

    def set_alias(self, telegram_id: int, alias: str):
        self._id_to_alias[telegram_id] = alias
        self._dump()

    @staticmethod
    def _load(alias_file_name: str) -> dict[int, str]:
        try:
            loaded_id_to_alias: dict[str, str] = json.load(open(alias_file_name))
        except Exception:
            loaded_id_to_alias: dict[str, str] = dict()
        res: dict[int, str] = dict()
        for key, value in loaded_id_to_alias.items():
            res[int(key)] = value
        return res

    def _dump(self):
        json.dump(self._id_to_alias, open(self._file_name_alias, 'w'))

    def get_alias_or_full_name(self, telegram_id: int, full_name: str) -> str:
        # if there is no alias, return full_name
        alias = self.get_alias(telegram_id=telegram_id)
        if alias is None:
            return full_name
        return alias

    def get_alias(self, telegram_id: int) -> str or None:
        if telegram_id in self._id_to_alias:
            return self._id_to_alias[telegram_id]
        return None

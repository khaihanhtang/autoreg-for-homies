import json


class IdentityManager:

    def __init__(self, alias_file_name):
        self._alias_file_name = alias_file_name
        self._id_to_alias: dict[int, str] = IdentityManager._load_from_file(alias_file_name=alias_file_name)

    def set_alias(self, telegram_id: int, alias: str):
        self._id_to_alias[telegram_id] = alias
        self._dump_to_file()

    @staticmethod
    def _load_from_file(alias_file_name: str) -> dict[int, str]:
        try:
            loaded_id_to_alias: dict[str, str] = json.load(open(alias_file_name))
        except Exception:
            loaded_id_to_alias: dict[str, str] = dict()
        res: dict[int, str] = dict()
        for key, value in loaded_id_to_alias.items():
            res[int(key)] = value
        return res

    def _dump_to_file(self):
        json.dump(self._id_to_alias, open(self._alias_file_name, 'w'))

    def get_alias_or_full_name(self, telegram_id: int, full_name: str) -> str:
        # if there is no alias, return full_name
        if telegram_id in self._id_to_alias:
            return self._id_to_alias[telegram_id]
        return full_name

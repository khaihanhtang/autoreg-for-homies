import asyncio
import json
import logging
import re
from collections.abc import Callable
from dataclasses import dataclass, field, replace
from datetime import datetime
from unicodedata import normalize

import httpx

from auto_registration_system.command import Command
from auto_registration_system.command_handler.handler_dereg import DeregHandler
from auto_registration_system.data_structure.registration_data import RegistrationData
from auto_registration_system.guide_language import GuideText, TEXT, fold_accents, question_language, validate_translations
from auto_registration_system.term import Term
from config import Config
from string_parser.string_parser import StringParser


@dataclass(frozen=True)
class CommandSuggestion:
    command: str
    description: GuideText | None = None
    is_template: bool = False
    copy_label: GuideText | None = None

    @property
    def button_label(self) -> GuideText:
        verb = self.command.split(maxsplit=1)[0]
        return self.copy_label or TEXT["copy_template" if self.is_template else "copy_command"].with_values(verb)


@dataclass(frozen=True)
class GuideReply:
    messages: tuple[GuideText, ...] = ()
    commands: tuple[CommandSuggestion, ...] = ()
    language: str | None = None
    translations: dict[str, str] = field(default_factory=dict)

    def render(self, text: GuideText) -> str:
        return text.render(self.language or "en", self.translations)


_COMMAND_TEMPLATES = {
    "available_places": (Command.COMMAND_AV, ""),
    "full_list": (Command.COMMAND_ALL, ""),
    "register_players": (Command.COMMAND_RG, " NAME SLOT"),
    "reserve_players": (Command.COMMAND_RS, " NAME SLOT"),
    "deregister_players": (Command.COMMAND_DRG, " NAME SLOT"),
    "view_alias": (Command.COMMAND_AKA, ""),
    "set_alias": (Command.COMMAND_AKA, " ALIAS"),
    "rename_existing_registration": (Command.COMMAND_ADMIN, ""),
    "registration_status": (Command.COMMAND_STATE, ""),
    "create_or_stage_list": (
        Command.COMMAND_NEW, f"\n{Term.DATE_VENUE} DATE at VENUE\n[a] 18:00-19:00 {Term.NUM_PLAYERS} 4",
    ),
    "schedule_once": (Command.COMMAND_NOTITIME, " HH:MM:SS DD/MM/YYYY"),
    "schedule_weekly": (Command.COMMAND_WEEKLYNOTITIME, " HH:MM:SS DD/MM/YYYY"),
    "schedule_test": (Command.COMMAND_TESTNOTITIME, " HH:MM:SS DD/MM/YYYY"),
    "cancel_once": (Command.COMMAND_NOTITIME, ""),
    "cancel_weekly": (Command.COMMAND_WEEKLYNOTITIME, ""),
    "cancel_test": (Command.COMMAND_TESTNOTITIME, ""),
    "cancel_unknown_mode": (Command.COMMAND_STATE, ""),
    "lock_registration": (Command.COMMAND_LOCK, ""),
    "unlock_registration": (Command.COMMAND_UNLOCK, ""),
    "reset_active_list": (Command.COMMAND_RESET, ""),
    "promote_all_reserves": (Command.COMMAND_ALLPENDING, ""),
    "activity_history": (Command.COMMAND_HISTORY, ""),
    "admin_list": (Command.COMMAND_ADMIN, ""),
    "request_admin_access": (Command.COMMAND_ADMIN, ""),
    "command_help": (Command.COMMAND_HELP, ""),
}
_GUIDE = {
    command_id: CommandSuggestion(f"/{verb}{arguments}", TEXT[command_id], is_template=bool(arguments))
    for command_id, (verb, arguments) in _COMMAND_TEMPLATES.items()
}
_PLAYER_FORMS = {"register_players", "reserve_players", "deregister_players"}
_SCHEDULE_FORMS = {"schedule_once", "schedule_weekly", "schedule_test"}
_SLOT_NAME_CONNECTORS = {"cua", "of", "the"}
_MAX_GUIDE_COMMANDS = 3

# Match complete requests for common commands before asking the model to interpret other wording.
_SELF_PLAYER_REQUESTS = {
    "register_players": (
        r"register me|sign me up|put me on (?:the )?(?:list|waitlist)|"
        r"(?:i (?:want|would like) to )?(?:register|sign up|play|join(?: the (?:list|waitlist))?)|"
        r"(?:(?:toi|minh|em) )?muon (?:choi|vao(?: danh sach(?: cho)?)?|dang k[yi])|"
        r"cho (?:toi|minh|em) vao(?: danh sach(?: cho)?)?|(?:(?:toi|minh|em) )?dang k[yi](?: cho (?:toi|minh|em))?"
    ),
    "reserve_players": (
        r"reserve (?:me|a spot for me)|add me (?:to|as) (?:the |a )?(?:reserve(?: list)?|regular reserve)|"
        r"(?:(?:toi|minh|em) )?(?:muon )?(?:lam du bi|dat cho du bi|vao danh sach du bi)|"
        r"cho (?:toi|minh|em) (?:lam du bi|vao danh sach du bi)"
    ),
    "deregister_players": (
        r"remove me(?: from (?:the )?(?:list|waitlist))?|deregister me|cancel my (?:sign[ -]?up|registration|reservation)|"
        r"(?:i (?:want|would like) to )?(?:deregister|leave)|"
        r"(?:(?:toi|minh|em) )?(?:muon )?(?:huy dang k[yi]|rut ten(?: toi|minh|em)?|xoa ten (?:toi|minh|em))"
    ),
}
_GUIDE_REQUESTS = {
    "available_places": (
        r"show (?:me )?(?:available|open) (?:slots|places|spots)|what slots are available|"
        r"(?:lam sao de )?xem (?:cac )?(?:khung gio|slot|suat) con cho"
    ),
    "full_list": r"show (?:me )?(?:the )?(?:full |current )?list|xem danh sach(?: hien tai)?",
    "registration_status": r"is registration locked|when is the next release|(?:xem )?trang thai dang k[yi]",
    "view_alias": r"what(?:'s| is) my alias|show my alias|xem (?:biet danh|aka)(?: cua toi)?",
    "set_alias": (
        r"(?:how (?:do|can) i |how to )?(?:set|change|update) my alias|"
        r"(?:(?:lam sao(?: de)?|cach) )?(?:dat|doi|sua) (?:biet danh|aka)(?: cua (?:toi|minh|em))?"
    ),
    "rename_existing_registration": (
        r"(?:how (?:do|can) i |how to )?(?:change|edit|fix|correct) (?:my |the )?name "
        r"(?:after (?:signing up|registering)|(?:in|on) (?:the )?"
        r"(?:(?:(?:active|current|registration|signup|sign-up) )?(?:list|roster)|slot [^\W_]+))|"
        r"(?:how (?:do|can) i |how to )?rename my (?:signup|registration)|"
        r"(?:(?:lam sao(?: de)?|cach) )?(?:doi|sua|thay doi) ten(?: (?:cua )?(?:minh|toi|em))? "
        r"(?:da dang k[yi]|(?:trong|tren) (?:danh sach(?: (?:minh |toi )?(?:da )?dang k[yi])?|slot(?: [^\W_]+)?))"
    ),
    "admin_list": r"who (?:are the (?:bot )?admins|is (?:the )?(?:bot )?admin)|(?:ai la|xem danh sach) admin(?: cua bot)?",
    "request_admin_access": (
        r"(?:how (?:do|can) i |how to )?(?:become (?:a |an )?(?:bot )?admin|(?:get|request) (?:bot )?admin (?:access|rights))|"
        r"(?:(?:lam sao(?: de)?|cach) )?(?:lam|tro thanh|duoc lam) admin(?: (?:cua )?bot)?"
    ),
}
_SLOT_KEYWORD = r"\s+(?:slot|khung(?: gi[ờo])?|su[ấa]t)\s+"
_SLOT_LABEL_AT_END = re.compile(
    _SLOT_KEYWORD + r"(?:\[([^\W_]+)\]|([^\W_]+))(?:\s+please)?$",
    re.IGNORECASE,
)
_SLOT_NAME_AT_END = re.compile(
    _SLOT_KEYWORD + r"(?:(?:c[óo] t[êe]n(?: l[àa])?|t[êe]n(?: l[àa])?|named|called|[ởo]|at)\s+)?(.+?)(?:\s+please)?$",
    re.IGNORECASE,
)
_SLOT_LOCATION_AT_END = re.compile(r"\s+(?:[ởo]|at)\s+(.+)$", re.IGNORECASE)
_VIETNAMESE_PLAY_AT_SLOT = (
    r"(?:(?:toi|minh|em) )?(?:muon )?(?:(?:vao|tham gia) )?"
    r"(?:danh cau(?: long)?|choi(?: cau(?: long)?)?)(?: voi (?:nhau|moi nguoi|cac ban)| cung nhau)?"
)
_WANT_TO_PLAY = re.compile(
    r"(?:i (?:want|would like) to play|(?:(?:t[ôo]i|m[ìi]nh|em) )?mu[ốo]n ch[ơo]i) (.+)",
    re.IGNORECASE,
)
_EXPLICIT_NAMES = re.compile(
    r"\s+(?:with the name|under the name|với tên|tên là)\s+(.+?)(?:\s+(?:for|in|to|from|into|vào|khỏi|ở))?$",
    re.IGNORECASE,
)
_VIETNAMESE_HOW_AT_END = re.compile(
    r"\s+(?:th[ìi] )?(?:ph[ảa]i )?l[àa]m (?:sao|th[ếe] n[àa]o)$", re.IGNORECASE,
)

_INSTRUCTIONS = (
    f"Select up to {_MAX_GUIDE_COMMANDS} command IDs for the user's question about the Homies badminton Telegram bot. "
    "Identify the language of the user's own question and return its two-letter ISO 639-1 code in language. "
    "Use en for ambiguous questions. Ignore Telegram command names, player names, and slot titles when identifying language. "
    "The question may be in Vietnamese or another language. Use command_help for a general request for bot help. "
    "Return an empty commands list for unrelated questions, even if they mention a bot command. "
    "Use check commands for live information. "
    "Use rename_existing_registration when the question asks to change a name already on the list. "
    "Use set_alias when the question asks to change the stored alias for future commands. "
    "Use request_admin_access for becoming a bot admin and admin_list for finding existing admins. "
    "Choose only entries that directly answer the question. "
    "Use register_players when the user asks how to join a badminton game at a named place. "
    "For register_players, reserve_players and deregister_players, put the slot label or the slot or venue name "
    "as the user wrote it first in args, "
    "then each explicitly named player or deregistration position as a separate string. Set use_sender to true "
    "when the sender wants to act for themselves without supplying their name. The bot fills in that name locally. "
    "For example, 'register Alex in slot a' gives args [\"a\", \"Alex\"] and use_sender false. "
    "'tôi muốn vào danh sách slot a' gives args [\"a\"] and use_sender true. "
    "For 'join the slot named Evening Session', use args [\"Evening Session\"] and use_sender true. "
    "If the slot is missing, use empty args and still set use_sender for a request about the sender. "
    "For a request to cancel the sender's signup without a slot, choose deregister_players with empty args "
    "and use_sender true so the bot can find their current signup. "
    "A phrase such as 'a slot' gives no label. Use use_sender false for commands other than these three. "
    "For set_alias use one alias, and for schedule commands use one complete HH:MM:SS DD/MM/YYYY value. "
    "Copy argument values verbatim from the question. Use empty args when the command has no parameters. "
    "If the user wants to cancel a release and the mode is unclear, "
    "select cancel_unknown_mode. The available commands are:\n"
    + "\n".join(f"{command_id}: {guide.command} - {TEXT[command_id].render('en', {})}"
                for command_id, guide in _GUIDE.items())
)
_RESPONSE_FORMAT = {
    "type": "json_schema",
    "json_schema": {
        "name": "bot_help_commands",
        "strict": True,
        "schema": {
            "type": "object",
            "properties": {
                "language": {"type": "string", "description": "Two-letter language code, or en if uncertain"},
                "commands": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "string", "enum": list(_GUIDE)},
                            "args": {"type": "array", "items": {"type": "string"}},
                            "use_sender": {"type": "boolean"},
                        },
                        "required": ["id", "args", "use_sender"],
                        "additionalProperties": False,
                    },
                },
            },
            "required": ["language", "commands"],
            "additionalProperties": False,
        },
    },
}
_TRANSLATION_FORMAT = {
    "type": "json_schema",
    "json_schema": {
        "name": "bot_guide_translations",
        "strict": True,
        "schema": {
            "type": "object",
            "properties": {"translations": {"type": "array", "items": {"type": "string"}}},
            "required": ["translations"],
            "additionalProperties": False,
        },
    },
}
_OUT_OF_SCOPE = GuideReply((TEXT["outside_scope"],))
_UNAVAILABLE = GuideReply((TEXT["unavailable"],))
_BUSY = GuideReply((TEXT["busy"],))
_MAX_QUESTION_LENGTH = 600
_REQUEST_SLOTS = asyncio.Semaphore(3)
_LOGGER = logging.getLogger(__name__)
_RESPONSE_ERRORS = (httpx.RequestError, TimeoutError, IndexError, KeyError, TypeError, ValueError)


def _slot_name_words(text: str) -> list[str]:
    words = re.findall(r"[^\W_]+", fold_accents(text))
    return [word for word in words if word not in _SLOT_NAME_CONNECTORS]


def _one_letter_off(word: str, title_word: str) -> bool:
    if min(len(word), len(title_word)) < 3 or not (word.isalpha() and title_word.isalpha()):
        return False

    first_difference = next(
        (index for index, (a, b) in enumerate(zip(word, title_word)) if a != b),
        min(len(word), len(title_word)),
    )
    tail, title_tail = word[first_difference:], title_word[first_difference:]
    if len(tail) == len(title_tail):
        return bool(tail) and tail[1:] == title_tail[1:]
    return tail[1:] == title_tail or tail == title_tail[1:]


def _slot_name_has_small_typos(reference: list[str], title: list[str]) -> bool:
    if len(reference) != len(title):
        return False
    differences = [(word, title_word) for word, title_word in zip(reference, title) if word != title_word]
    # Keep at least one exact word and at most two one-letter errors in the full name.
    return 0 < len(differences) <= 2 and len(differences) < len(title) and all(
        _one_letter_off(word, title_word) for word, title_word in differences
    )


def _resolve_slot_label(
        reference: str, active_list: RegistrationData | None, *, by_name: bool,
) -> str | CommandSuggestion | None:
    label = reference.lower()
    is_label = label.isalnum() and label.islower()
    if not by_name and is_label and (active_list is None or active_list.get_slot(label) is not None):
        return label

    reference = normalize("NFC", reference.casefold())
    slots = active_list.collect_all_slots_with_labels() if active_list is not None else []
    names = [(label, slot, normalize("NFC", " ".join(slot.slot_name.casefold().split()))) for label, slot in slots]
    matches = [(label, slot) for label, slot, name in names if name == reference]
    if not matches:
        folded_reference = fold_accents(reference)
        matches = [(label, slot) for label, slot, name in names if fold_accents(name) == folded_reference]
    if not matches:
        reference_words = _slot_name_words(reference)
        if len(reference_words) > 1:
            candidates = [(label, slot, _slot_name_words(name)) for label, slot, name in names]
            sorted_reference = sorted(reference_words)
            matches = [(label, slot) for label, slot, words in candidates if sorted(words) == sorted_reference]
            if not matches:
                # Require a complete phrase in the title before matching a shortened name.
                phrase = " ".join(reference_words)
                matches = [(label, slot) for label, slot, words in candidates if f" {phrase} " in f" {' '.join(words)} "]
            if not matches:
                matches = [
                    (label, slot) for label, slot, words in candidates
                    if _slot_name_has_small_typos(reference_words, words)
                ]

    if not matches:
        return None
    if active_list is not None and len(matches) == 1:
        matched_label, matched_slot = matches[0]
        # Regular commands resolve a label to its first slot. Only suggest it if it points to the matching slot.
        if active_list.get_slot(matched_label) is matched_slot:
            return matched_label
    return replace(
        _GUIDE["full_list"],
        description=TEXT["multiple_matching_slots"],
    )


def _player_sender_name(sender_name: str | None) -> str | None:
    if (sender_name and sender_name.isprintable() and "," not in sender_name
            and any(letter.isalpha() for letter in sender_name)):
        return " ".join(sender_name.split())
    return None


def _build_player_command(
        command_id: str, slot: str, names: list[str], sender_name: str | None,
) -> CommandSuggestion:
    suggestion = _GUIDE[command_id]
    if any("," in name or (not any(letter.isalpha() for letter in name)
                           and not (command_id == "deregister_players" and name.isdecimal() and int(name) > 0))
           for name in names):
        return suggestion
    if name := _player_sender_name(sender_name):
        names = [name, *names]
    verb = suggestion.command.split(maxsplit=1)[0]
    command = f"{verb} {', '.join(names) or 'NAME'} {slot or 'SLOT'}"
    return replace(suggestion, command=command, is_template=not (names and slot))


def _deregister_my_signup(sender_name: str | None, active_list: RegistrationData | None) -> GuideReply | None:
    name = _player_sender_name(sender_name)
    if name is None or active_list is None:
        return None

    lookup_name = StringParser.split_names(name)[0]
    slots = DeregHandler.search_for_slots_able_to_be_deregistered(lookup_name, active_list)
    if not slots:
        return GuideReply((TEXT["no_signup"],), (_GUIDE["full_list"],))
    if any(active_list.get_slot(label) is not slot for label, slot in slots):
        return GuideReply((TEXT["shared_slot_label"],), (_GUIDE["full_list"],))
    if len(slots) > _MAX_GUIDE_COMMANDS:
        return GuideReply((TEXT["many_signups"],), (_GUIDE["full_list"],))

    commands = tuple(
        replace(
            _build_player_command("deregister_players", label, [], name),
            description=TEXT["leave_slot"].with_values(label, slot.slot_name),
            copy_label=TEXT["copy_leave_slot"].with_values(f"/{Command.COMMAND_DRG}", label),
        )
        for label, slot in slots
    )
    return GuideReply((TEXT["choose_slot"],) if len(commands) > 1 else (), commands)


def _build_command(
        command_id: str, args: list[str], question: str, *, sender_name: str | None = None,
        active_list: RegistrationData | None = None, slot_by_name: bool = False,
) -> CommandSuggestion:
    suggestion = _GUIDE[command_id]
    if not suggestion.is_template or any(not value.isprintable() for value in args):
        return suggestion

    # Only fill templates with values the user actually supplied, keeping each command on one line.
    values = [" ".join(value.split()) for value in args]
    normalized_question = normalize("NFC", " ".join(question.casefold().split()))
    if any(not value or not re.search(rf"(?<!\w){re.escape(normalize('NFC', value.casefold()))}(?!\w)", normalized_question)
           for value in values):
        return suggestion

    if command_id in _PLAYER_FORMS:
        slot = _resolve_slot_label(values[0], active_list, by_name=slot_by_name) if values else ""
        if slot is None:
            return replace(_GUIDE["full_list"], description=TEXT["unknown_slot"])
        if isinstance(slot, CommandSuggestion):
            return slot
        return _build_player_command(command_id, slot, values[1:], sender_name)

    verb = suggestion.command.split(maxsplit=1)[0]
    if command_id == "set_alias" and len(values) == 1 and not any(mark in values[0] for mark in ",@"):
        command = f"{verb} {values[0]}"
    elif command_id in _SCHEDULE_FORMS and len(values) == 1:
        try:
            scheduled_time = datetime.strptime(values[0], Config.input_time_format)
        except ValueError:
            return suggestion
        command = f"{verb} {scheduled_time.strftime(Config.input_time_format)}"
    else:
        return suggestion
    return replace(suggestion, command=command, is_template=False)


def _reply_for_command(
        command_id: str, args: list[str], question: str, *, sender_name: str | None,
        active_list: RegistrationData | None, slot_by_name: bool = False,
) -> GuideReply:
    if command_id == "deregister_players" and not args:
        reply = _deregister_my_signup(sender_name, active_list)
        if reply is not None:
            return reply
    suggestion = _build_command(
        command_id, args, question, sender_name=sender_name,
        active_list=active_list, slot_by_name=slot_by_name,
    )
    return GuideReply(commands=(suggestion,))


def _local_reply(
        question: str, sender_name: str | None, active_list: RegistrationData | None = None,
) -> GuideReply | None:
    text = normalize("NFC", " ".join(question.split())).rstrip(" ?!.？！。")
    text = _VIETNAMESE_HOW_AT_END.sub("", text)
    full_intent = fold_accents(text)
    for command_id, pattern in _GUIDE_REQUESTS.items():
        if re.fullmatch(pattern, full_intent):
            return GuideReply(commands=(_GUIDE[command_id],))

    label_match = _SLOT_LABEL_AT_END.search(text)
    name_match = (_SLOT_NAME_AT_END.search(text) or _SLOT_LOCATION_AT_END.search(text)) if label_match is None else None
    slot_match = label_match or name_match
    intent = text[:slot_match.start()] if slot_match else text
    explicit_names = _EXPLICIT_NAMES.search(intent) if slot_match else None
    if explicit_names:
        intent = intent[:explicit_names.start()]
    intent = fold_accents(intent)
    for command_id, pattern in _SELF_PLAYER_REQUESTS.items():
        if command_id == "register_players" and name_match:
            pattern += f"|{_VIETNAMESE_PLAY_AT_SLOT}"
        if re.fullmatch(
                r"(?:(?:can|could|would) you (?:help )?|how (?:do|can) i |how to |(?:lam sao|lam the nao) de |cach )?"
                rf"(?:please )?(?:{pattern})"
                r"(?: (?:for|in|to|from|into|vao|khoi|o))?(?: the)?",
                intent,
        ):
            if label_match:
                args = [label_match.group(1) or label_match.group(2)]
            elif name_match:
                args = [name_match.group(1).strip('"“”')]
            else:
                args = []
            if explicit_names:
                args.extend(explicit_names.group(1).split(","))
                sender_name = None
            return _reply_for_command(
                command_id, args, question, sender_name=sender_name,
                active_list=active_list, slot_by_name=name_match is not None,
            )

    if active_list is not None and (play_request := _WANT_TO_PLAY.fullmatch(text)):
        slot = _resolve_slot_label(play_request.group(1).strip('"“”'), active_list, by_name=True)
        if slot is not None:
            suggestion = _build_player_command("register_players", slot, [], sender_name) if isinstance(slot, str) else slot
            return GuideReply(commands=(suggestion,))

    return None


async def _request_completion(
        *, account_id: str, api_token: str, system_prompt: str, content: str,
        response_format: dict, max_completion_tokens: int = 512,
) -> dict:
    async with _REQUEST_SLOTS, asyncio.timeout(15), httpx.AsyncClient(timeout=15.0) as client:
        response = await client.post(
            f"https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_token}"},
            json={
                "model": "@cf/google/gemma-4-26b-a4b-it",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": content},
                ],
                "max_completion_tokens": max_completion_tokens,
                "temperature": 0,
                "chat_template_kwargs": {"enable_thinking": False},
                "response_format": response_format,
                "store": False,
            },
        )
        response.raise_for_status()
    choice = response.json()["choices"][0]
    if choice["finish_reason"] != "stop":
        raise ValueError("Incomplete guide response")
    result = json.loads(choice["message"]["content"])
    if not isinstance(result, dict):
        raise ValueError("Invalid guide response")
    return result


async def _select_reply(
        question: str, *, account_id: str, api_token: str, sender_name: str | None = None,
        get_active_list: Callable[[], RegistrationData | None] | None = None,
) -> GuideReply:
    if not question:
        return GuideReply(
            (TEXT["usage"],),
            (CommandSuggestion(f"/{Command.COMMAND_AI} How do I see available slots?"),),
        )
    if len(question) > _MAX_QUESTION_LENGTH:
        return GuideReply((TEXT["question_length"].with_values(_MAX_QUESTION_LENGTH),))

    local_reply = _local_reply(question, sender_name, get_active_list() if get_active_list else None)
    if local_reply is not None:
        return local_reply
    if _REQUEST_SLOTS.locked():
        return _BUSY

    language = None
    try:
        result = await _request_completion(
            account_id=account_id, api_token=api_token, system_prompt=_INSTRUCTIONS,
            content=question, response_format=_RESPONSE_FORMAT,
        )
        if isinstance(result.get("language"), str) and re.fullmatch("[a-z]{2}", result["language"].lower()):
            language = result["language"].lower()
        commands = result["commands"]
        if not isinstance(commands, list) or len(commands) > _MAX_GUIDE_COMMANDS:
            raise ValueError("Invalid guide response")
        if not commands:
            return replace(_OUT_OF_SCOPE, language=language)

        active_list = get_active_list() if get_active_list else None
        suggestions = {}
        messages = []
        for item in commands:
            command_id, args, use_sender = item["id"], item["args"], item["use_sender"]
            if (command_id not in _GUIDE or not isinstance(args, list) or not isinstance(use_sender, bool)
                    or any(not isinstance(arg, str) for arg in args)):
                raise ValueError("Invalid guide command")
            reply = _reply_for_command(
                command_id, args, question, sender_name=sender_name if use_sender else None,
                active_list=active_list,
            )
            messages.extend(reply.messages)
            for suggestion in reply.commands:
                suggestions.setdefault(suggestion.command, suggestion)
        return GuideReply(tuple(dict.fromkeys(messages)), tuple(suggestions.values()), language=language)
    except httpx.HTTPStatusError as error:
        if error.response.status_code == 429:
            return _BUSY
        _LOGGER.warning("Cloudflare Workers AI guide request returned HTTP %s", error.response.status_code)
    except _RESPONSE_ERRORS as error:
        _LOGGER.warning("Cloudflare Workers AI guide request failed (%s)", type(error).__name__)
    return replace(_UNAVAILABLE, language=language)


async def answer_bot_question(
        question: str, *, account_id: str, api_token: str, sender_name: str | None = None,
        get_active_list: Callable[[], RegistrationData | None] | None = None,
) -> GuideReply:
    question = question.strip()
    reply = await _select_reply(
        question, account_id=account_id, api_token=api_token, sender_name=sender_name,
        get_active_list=get_active_list,
    )
    language = reply.language or question_language(question)
    if language in {"en", "vi", "zh"}:
        return replace(reply, language=language)
    if _REQUEST_SLOTS.locked():
        return replace(reply, language="en")

    text = list(reply.messages)
    for suggestion in reply.commands:
        if suggestion.description is not None:
            text.append(suggestion.description)
        text.append(suggestion.button_label)
    if any(suggestion.is_template for suggestion in reply.commands):
        text.append(TEXT["replace_placeholders"])
    # Translate the built-in templates before inserting any names, slot titles, or commands.
    templates = list(dict.fromkeys(item.english for item in text))
    try:
        result = await _request_completion(
            account_id=account_id, api_token=api_token,
            system_prompt=(
                "Translate each English template into the language identified by the supplied two-letter code. "
                "Keep the template order, meaning, and numbered placeholders such as {0} exactly. "
                "Only return translations of the supplied text."
            ),
            content=json.dumps({"language": language, "templates": templates}),
            response_format=_TRANSLATION_FORMAT, max_completion_tokens=1024,
        )
        translations = validate_translations(templates, result["translations"])
        return replace(reply, language=language, translations=translations)
    except (httpx.HTTPStatusError, *_RESPONSE_ERRORS) as error:
        _LOGGER.warning("Cloudflare Workers AI guide translation failed (%s)", type(error).__name__)
        return replace(reply, language="en")

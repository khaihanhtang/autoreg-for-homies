import asyncio
import json
import logging
import re
from collections.abc import Callable
from dataclasses import dataclass, replace
from datetime import datetime
from unicodedata import combining, normalize

import httpx

from auto_registration_system.command import Command
from auto_registration_system.data_structure.registration_data import RegistrationData
from auto_registration_system.term import Term
from config import Config


@dataclass(frozen=True)
class CommandSuggestion:
    command: str
    description: str
    is_template: bool = False


@dataclass(frozen=True)
class GuideReply:
    message: str = ""
    commands: tuple[CommandSuggestion, ...] = ()


_GUIDE = {
    "available_places": CommandSuggestion(f"/{Command.COMMAND_AV}", "Shows open places in the registration group."),
    "full_list": CommandSuggestion(f"/{Command.COMMAND_ALL}", "Shows all slots, players, and reserves."),
    "register_players": CommandSuggestion(
        f"/{Command.COMMAND_RG} NAME SLOT",
        "Send in the registration group. Separate multiple names with commas. "
        "If the slot is full, players join the pending waitlist and move up as places open.",
        is_template=True,
    ),
    "reserve_players": CommandSuggestion(
        f"/{Command.COMMAND_RS} NAME SLOT",
        "Adds regular reserves in the registration group. An admin can move them into the lineup.",
        is_template=True,
    ),
    "deregister_players": CommandSuggestion(
        f"/{Command.COMMAND_DRG} NAME SLOT",
        "Removes a player from the slot or its waitlist. You can also use the player's position in the lineup.",
        is_template=True,
    ),
    "view_alias": CommandSuggestion(f"/{Command.COMMAND_AKA}", "Shows your current alias."),
    "set_alias": CommandSuggestion(f"/{Command.COMMAND_AKA} ALIAS", "Sets your alias.", is_template=True),
    "registration_status": CommandSuggestion(
        f"/{Command.COMMAND_STATE}", "Shows whether registration is locked, whether the list has slots, and the next release."
    ),
    "create_or_stage_list": CommandSuggestion(
        f"/{Command.COMMAND_NEW}\n{Term.DATE_VENUE} DATE at VENUE\n[a] 18:00-19:00 {Term.NUM_PLAYERS} 4",
        "Admins can send this in the registration group to replace the active list or in a direct message to stage it.",
        is_template=True,
    ),
    "schedule_once": CommandSuggestion(
        f"/{Command.COMMAND_NOTITIME} HH:MM:SS DD/MM/YYYY",
        "Schedules a one-time release. Admins should stage the list first and enter a future Singapore time.",
        is_template=True,
    ),
    "schedule_weekly": CommandSuggestion(
        f"/{Command.COMMAND_WEEKLYNOTITIME} HH:MM:SS DD/MM/YYYY",
        "Schedules a weekly release. Admins should stage the list first and enter a future Singapore time.",
        is_template=True,
    ),
    "schedule_test": CommandSuggestion(
        f"/{Command.COMMAND_TESTNOTITIME} HH:MM:SS DD/MM/YYYY",
        "Schedules test releases every 5 minutes. Admins should stage the list first and enter a future Singapore time.",
        is_template=True,
    ),
    "cancel_once": CommandSuggestion(f"/{Command.COMMAND_NOTITIME}", "Turns off the one-time release schedule. Admin only."),
    "cancel_weekly": CommandSuggestion(f"/{Command.COMMAND_WEEKLYNOTITIME}", "Turns off the weekly schedule. Admin only."),
    "cancel_test": CommandSuggestion(f"/{Command.COMMAND_TESTNOTITIME}", "Turns off the test schedule. Admin only."),
    "cancel_unknown_mode": CommandSuggestion(
        f"/{Command.COMMAND_STATE}", "Check the active release mode first. An admin can cancel it by sending that scheduling command by itself."
    ),
    "lock_registration": CommandSuggestion(f"/{Command.COMMAND_LOCK}", "Locks registration. Admin only."),
    "unlock_registration": CommandSuggestion(f"/{Command.COMMAND_UNLOCK}", "Opens registration. Admin only."),
    "reset_active_list": CommandSuggestion(f"/{Command.COMMAND_RESET}", "Clears the active list. Admin only."),
    "promote_all_reserves": CommandSuggestion(
        f"/{Command.COMMAND_ALLPENDING}",
        "Moves all regular reserves onto the pending waitlist and fills open places. Admin only.",
    ),
    "activity_history": CommandSuggestion(f"/{Command.COMMAND_HISTORY}", "Retrieves the activity history. Admin only."),
    "admin_list": CommandSuggestion(f"/{Command.COMMAND_ADMIN}", "Shows who the admins are."),
    "command_help": CommandSuggestion(f"/{Command.COMMAND_HELP}", "Shows the bot's command guide."),
}
_PLAYER_FORMS = {"register_players", "reserve_players", "deregister_players"}
_SCHEDULE_FORMS = {"schedule_once", "schedule_weekly", "schedule_test"}

# Match complete requests for common commands before asking the model to interpret other wording.
_SELF_PLAYER_REQUESTS = {
    "register_players": (
        r"register me|sign me up|put me on (?:the )?(?:list|waitlist)|"
        r"(?:i (?:want|would like) to )?(?:register|sign up|join(?: the (?:list|waitlist))?)|"
        r"(?:(?:toi|minh|em) )?muon (?:vao(?: danh sach(?: cho)?)?|dang k[yi])|"
        r"cho (?:toi|minh|em) vao(?: danh sach(?: cho)?)?|dang k[yi](?: cho (?:toi|minh|em))?"
    ),
    "reserve_players": (
        r"reserve (?:me|a spot for me)|add me (?:to|as) (?:the |a )?(?:reserve(?: list)?|regular reserve)|"
        r"(?:(?:toi|minh|em) )?(?:muon )?(?:lam du bi|dat cho du bi|vao danh sach du bi)|"
        r"cho (?:toi|minh|em) (?:lam du bi|vao danh sach du bi)"
    ),
    "deregister_players": (
        r"remove me(?: from (?:the )?(?:list|waitlist))?|deregister me|cancel my (?:signup|registration)|"
        r"(?:i (?:want|would like) to )?(?:deregister|leave)|"
        r"(?:(?:toi|minh|em) )?(?:muon )?(?:huy dang k[yi]|rut ten(?: toi|minh|em)?|xoa ten (?:toi|minh|em))"
    ),
}
_READ_REQUESTS = {
    "available_places": (
        r"show (?:me )?(?:available|open) (?:slots|places|spots)|what slots are available|"
        r"(?:lam sao de )?xem (?:cac )?(?:khung gio|slot|suat) con cho"
    ),
    "full_list": r"show (?:me )?(?:the )?(?:full |current )?list|xem danh sach(?: hien tai)?",
    "registration_status": r"is registration locked|when is the next release|(?:xem )?trang thai dang k[yi]",
    "view_alias": r"what(?:'s| is) my alias|show my alias|xem (?:biet danh|aka)(?: cua toi)?",
}
_SLOT_KEYWORD = r"\s+(?:slot|khung(?: gi[ờo])?|su[ấa]t)\s+"
_SLOT_LABEL_AT_END = re.compile(
    _SLOT_KEYWORD + r"(?:\[([^\W_]+)\]|([^\W_]+))(?:\s+please)?$",
    re.IGNORECASE,
)
_SLOT_NAME_AT_END = re.compile(
    _SLOT_KEYWORD + r"(?:(?:c[óo] t[êe]n(?: l[àa])?|t[êe]n(?: l[àa])?|named|called)\s+)?(.+?)(?:\s+please)?$",
    re.IGNORECASE,
)
_EXPLICIT_NAMES = re.compile(
    r"\s+(?:with the name|under the name|với tên|tên là)\s+(.+?)(?:\s+(?:for|in|to|from|into|vào|khỏi|ở))?$",
    re.IGNORECASE,
)

_INSTRUCTIONS = (
    "Select up to three command IDs for the user's question about the Homies badminton Telegram bot. "
    "The question may be in Vietnamese or another language. Use command_help for a general request for bot help. "
    "Return an empty commands list for unrelated questions, even if they mention a bot command. "
    "Use check commands for live information. "
    "For register_players, reserve_players and deregister_players, put the slot label or full slot name first in args, "
    "then each explicitly named player or deregistration position as a separate string. Set use_sender to true "
    "when the sender wants to act for themselves without supplying their name. The bot fills in that name locally. "
    "For example, 'register Alex in slot a' gives args [\"a\", \"Alex\"] and use_sender false. "
    "'tôi muốn vào danh sách slot a' gives args [\"a\"] and use_sender true. "
    "For 'join the slot named Evening Session', use args [\"Evening Session\"] and use_sender true. "
    "If the slot is missing, use empty args and still set use_sender for a request about the sender. "
    "A phrase such as 'a slot' gives no label. Use use_sender false for commands other than these three. "
    "For set_alias use one alias, and for schedule commands use one complete HH:MM:SS DD/MM/YYYY value. "
    "Copy argument values verbatim from the question. Use empty args when the command has no parameters. "
    "If the user wants to cancel a release and the mode is unclear, "
    "select cancel_unknown_mode. The available commands are:\n"
    + "\n".join(f"{command_id}: {guide.command} - {guide.description}" for command_id, guide in _GUIDE.items())
)
_RESPONSE_FORMAT = {
    "type": "json_schema",
    "json_schema": {
        "name": "bot_help_commands",
        "strict": True,
        "schema": {
            "type": "object",
            "properties": {
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
            "required": ["commands"],
            "additionalProperties": False,
        },
    },
}
_OUT_OF_SCOPE = GuideReply("That question is outside this bot's scope. I can help with badminton registration commands.")
_UNAVAILABLE = GuideReply("I can only help with using this registration bot. AI help is unavailable right now.")
_BUSY = GuideReply("AI help is busy. Try again later.")
_MAX_QUESTION_LENGTH = 600
_REQUEST_SLOTS = asyncio.Semaphore(3)
_LOGGER = logging.getLogger(__name__)


def _fold_accents(text: str) -> str:
    folded = normalize("NFD", text.casefold().replace("đ", "d"))
    return "".join(char for char in folded if not combining(char))


def _resolve_slot_label(
        reference: str, active_list: RegistrationData | None, *, by_name: bool,
) -> str | CommandSuggestion:
    label = reference.lower()
    is_label = label.isalnum() and label.islower()
    if not by_name and is_label and (active_list is None or active_list.get_slot(label) is not None):
        return label

    reference = normalize("NFC", reference.casefold())
    slots = active_list.collect_all_slots_with_labels() if active_list is not None else []
    names = [(label, slot, normalize("NFC", " ".join(slot.slot_name.casefold().split()))) for label, slot in slots]
    matches = [(label, slot) for label, slot, name in names if name == reference]
    if not matches:
        folded_reference = _fold_accents(reference)
        matches = [(label, slot) for label, slot, name in names if _fold_accents(name) == folded_reference]

    if active_list is not None and len(matches) == 1:
        matched_label, matched_slot = matches[0]
        # Regular commands resolve a label to its first slot. Only suggest it if it points to the matching slot.
        if active_list.get_slot(matched_label) is matched_slot:
            return matched_label
    explanation = (
        "Several active slots share that name or label. Check the list in the registration group."
        if matches else "I couldn't find that slot. Check the active list in the registration group."
    )
    return replace(_GUIDE["full_list"], description=explanation)


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

    verb = suggestion.command.split(maxsplit=1)[0]
    if command_id in _PLAYER_FORMS:
        slot = _resolve_slot_label(values[0], active_list, by_name=slot_by_name) if values else ""
        if isinstance(slot, CommandSuggestion):
            return slot
        names = values[1:]
        if any("," in name or (not any(letter.isalpha() for letter in name)
                               and not (command_id == "deregister_players" and name.isdecimal() and int(name) > 0))
               for name in names):
            return suggestion
        if (sender_name and sender_name.isprintable() and "," not in sender_name
                and any(letter.isalpha() for letter in sender_name)):
            names.insert(0, " ".join(sender_name.split()))
        command = f"{verb} {', '.join(names) or 'NAME'} {slot or 'SLOT'}"
        return replace(suggestion, command=command, is_template=not (names and slot))
    elif command_id == "set_alias" and len(values) == 1 and not any(mark in values[0] for mark in ",@"):
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


def _local_reply(
        question: str, sender_name: str | None, active_list: RegistrationData | None = None,
) -> GuideReply | None:
    text = normalize("NFC", " ".join(question.split())).rstrip(" ?!.？！。")
    full_intent = _fold_accents(text)
    for command_id, pattern in _READ_REQUESTS.items():
        if re.fullmatch(pattern, full_intent):
            return GuideReply(commands=(_GUIDE[command_id],))

    label_match = _SLOT_LABEL_AT_END.search(text)
    name_match = _SLOT_NAME_AT_END.search(text) if label_match is None else None
    slot_match = label_match or name_match
    intent = text[:slot_match.start()] if slot_match else text
    explicit_names = _EXPLICIT_NAMES.search(intent) if slot_match else None
    if explicit_names:
        intent = intent[:explicit_names.start()]
    intent = _fold_accents(intent)
    for command_id, pattern in _SELF_PLAYER_REQUESTS.items():
        if re.fullmatch(
                rf"(?:(?:can|could|would) you (?:help )?)?(?:please )?(?:{pattern})"
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
            suggestion = _build_command(
                command_id, args, question, sender_name=sender_name,
                active_list=active_list, slot_by_name=name_match is not None,
            )
            return GuideReply(commands=(suggestion,))

    return None


async def answer_bot_question(
        question: str, *, account_id: str, api_token: str, sender_name: str | None = None,
        get_active_list: Callable[[], RegistrationData | None] | None = None,
) -> GuideReply:
    question = question.strip()
    if not question:
        return GuideReply(
            "Ask how to use the bot. Questions that need AI are sent to Cloudflare Workers AI.",
            (CommandSuggestion(f"/{Command.COMMAND_AI} How do I see available slots?", ""),),
        )
    if len(question) > _MAX_QUESTION_LENGTH:
        return GuideReply(f"Keep your question to {_MAX_QUESTION_LENGTH} characters or fewer.")

    local_reply = _local_reply(question, sender_name, get_active_list() if get_active_list else None)
    if local_reply is not None:
        return local_reply
    if _REQUEST_SLOTS.locked():
        return _BUSY

    try:
        async with _REQUEST_SLOTS, asyncio.timeout(15), httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(
                f"https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/v1/chat/completions",
                headers={"Authorization": f"Bearer {api_token}"},
                json={
                    "model": "@cf/google/gemma-4-26b-a4b-it",
                    "messages": [
                        {"role": "system", "content": _INSTRUCTIONS},
                        {"role": "user", "content": question},
                    ],
                    "max_completion_tokens": 512,
                    "temperature": 0,
                    "chat_template_kwargs": {"enable_thinking": False},
                    "response_format": _RESPONSE_FORMAT,
                    "store": False,
                },
            )
            response.raise_for_status()
        choice = response.json()["choices"][0]
        commands = json.loads(choice["message"]["content"])["commands"]
        if choice["finish_reason"] != "stop" or not isinstance(commands, list) or len(commands) > 3:
            raise ValueError("Invalid guide response")
        if not commands:
            return _OUT_OF_SCOPE

        active_list = get_active_list() if get_active_list else None
        suggestions = {}
        for item in commands:
            command_id, args, use_sender = item["id"], item["args"], item["use_sender"]
            if (command_id not in _GUIDE or not isinstance(args, list) or not isinstance(use_sender, bool)
                    or any(not isinstance(arg, str) for arg in args)):
                raise ValueError("Invalid guide command")
            suggestion = _build_command(
                command_id, args, question, sender_name=sender_name if use_sender else None,
                active_list=active_list,
            )
            suggestions.setdefault(suggestion.command, suggestion)
        return GuideReply(commands=tuple(suggestions.values()))
    except httpx.HTTPStatusError as error:
        if error.response.status_code == 429:
            return _BUSY
        _LOGGER.warning("Cloudflare Workers AI guide request returned HTTP %s", error.response.status_code)
    except (httpx.RequestError, TimeoutError, IndexError, KeyError, TypeError, ValueError) as error:
        _LOGGER.warning("Cloudflare Workers AI guide request failed (%s)", type(error).__name__)
    return _UNAVAILABLE

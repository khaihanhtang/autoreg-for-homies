from auto_registration_system.data_structure.registration_data import RegistrationData
from string_parser.string_parser import StringParser
from ..data_structure.reservation import Reservation
from ..data_structure.slot_manager import SlotManager
from ..exception.error_maker import ErrorMaker


class DeregHandler:
    @staticmethod
    def handle(message: str, data: RegistrationData) -> str:
        original_message = message
        message = StringParser.remove_command(message=message)
        try:
            slot_label = StringParser.get_last_word(message=message)
            current_message = StringParser.remove_last_word(message=message)
        except Exception:
            raise ErrorMaker.make_syntax_error_exception(message=original_message)

        players: list[str] = StringParser.split_names(current_message)

        response: str = ""
        count_processed: int = 0
        slot: SlotManager = data.get_slot(slot_label=slot_label)
        if slot is None:
            return f"Cannot find slot {slot_label}\\!"
        for name in players:
            if len(name) > 0:
                count_processed += 1
                try:
                    index = int(name) - 1
                    if index < 0 or index >= slot.num_players:
                        response += f"Position {index + 1} is not valid\\!\n"
                    elif index >= len(slot.players) or slot.players[index] == "":
                        response += f"Position {index + 1} has been removed or does not exist\\!\n"
                    else:
                        response += (f"{slot.players[index]} \\(from position {index + 1}\\) "
                                     + f"has been removed from slot {slot_label}\\!\n")
                        slot.players[index] = ""
                except ValueError:
                    found: bool = False
                    for i, player_name in enumerate(slot.players):
                        if name == player_name:
                            slot.players[i] = ""
                            found = True
                            break
                    if not found:
                        for i, reservation in enumerate(slot.reservations):
                            if reservation.name == name:
                                slot.reservations[i] = Reservation(name="", is_pending=False)
                                found = True
                                break
                    if found:
                        response += f"{
                            StringParser.replace_escape_characters_for_markdown(name)
                        } has been removed from slot {slot_label}\\!\n"
                    else:
                        response += f"{
                            StringParser.replace_escape_characters_for_markdown(name)
                        } does not exist in slot {slot_label}\\!\n"
        # clean empty elements
        new_players: list[str] = list()
        new_reservations: list[Reservation] = list()
        for player in slot.players:
            if player != "":
                new_players.append(player)
        for reservation in slot.reservations:
            if reservation is not None and reservation.name != "":
                new_reservations.append(reservation)
        slot.players = new_players
        slot.reservations = new_reservations
        slot.restructure()
        if count_processed == 0:
            return "There is nothing changed\\!"

        return response

    @staticmethod
    def make_suggestion(command_string: str, id_string: str, data: RegistrationData) -> str or None:
        res: str = ""
        count: int = 0
        slots_able_to_be_deregistered = DeregHandler.search_for_slots_able_to_be_deregistered(
            id_string=id_string,
            data=data
        )
        for slot_label, slot in slots_able_to_be_deregistered:
            res += f"{count + 1}\\. `/{command_string} "
            res += f"{StringParser.replace_escape_characters_for_markdown(message=id_string)} {slot_label}`\n"
            count += 1
        if len(res) == 0:
            return None
        return f"You can try the following commands \\(hold to copy\\):\n{res}"

    @staticmethod
    def search_for_slots_able_to_be_deregistered(id_string: str, data: RegistrationData) -> list[(str, SlotManager)]:
        res: list[(str, SlotManager)] = list()
        for slot_label, slot in data.collect_all_slots_with_labels():
            if slot.is_in_any_list(proposed_name=id_string):
                res.append((slot_label, slot))
        return res

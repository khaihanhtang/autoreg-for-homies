from auto_registration_system.data_structure.registration_data import RegistrationData
from auto_registration_system.string_parser.string_parser import StringParser
from ..data_structure.reservation import Reservation
from ..data_structure.slot_manager import SlotManager
from ..exception.error_maker import ErrorMaker


class DeregHandler:
    @staticmethod
    def handle(message: str, data: RegistrationData):
        try:
            slot_label = StringParser.get_last_word(message=message)
            current_message = StringParser.remove_last_word(message=message)
        except:
            raise ErrorMaker.make_syntax_error_exception(message=message)

        players: list[str] = StringParser.split_names(current_message)

        response: str = ""
        count_processed: int = 0
        slot: SlotManager = data.get_slot(slot_label=slot_label)
        if slot is None:
            return f"Không tìm thấy slot {slot_label}!"
        for name in players:
            if len(name) > 0:
                count_processed += 1
                try:
                    index = int(name) - 1
                    if index < 0 or index >= slot.max_num_players:
                        response += f"Chỉ số '{index + 1}' không phù hợp!\n"
                    elif slot.players[index] == "":
                        response += f"Chỉ số '{index + 1}' đã bị xóa!\n"
                    else:
                        response += f"{name} (từ chỉ số {index + 1}) vừa được xóa khỏi slot {slot_label}!\n"
                        slot.players[index] = ""
                except Exception:
                    found: bool = False
                    for i, player_name in enumerate(slot.players):
                        if name == player_name:
                            slot.players[i] = ""
                            found = True
                            break
                    if not found:
                        for i, reservation in enumerate(slot.reservations):
                            if reservation.name == name:
                                slot.reservations[i] = ""
                                found = True
                                break
                    if found:
                        response += f"{name} vừa được xóa khỏi slot {slot_label}!\n"
                    else:
                        response += f"{name} không tồn tại trong slot {slot_label}!\n"
        # TODO: clean empty elements
        new_players = list[str]
        new_reservations = list[Reservation]
        for player in slot.players:
            if player != "":
                new_players.append(player)
        for reservation in slot.reservations:
            if reservation.name != "":
                new_reservations.append(reservation)
        slot.players = new_players
        slot.reservations = new_reservations
        if count_processed == 0:
            return "Không có gì thay đổi!"

        data.move_all_playable_players()

        return response

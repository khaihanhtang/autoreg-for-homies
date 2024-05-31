from auto_registration_system.data_structure.registration_data import RegistrationData


class AllplayableHandler:
    @staticmethod
    def handle(message: str, data: RegistrationData) -> str:
        for datevenue in data.bookings_by_datevenue:
            for slot_label in data.bookings_by_datevenue[datevenue]:
                for reservation in data.bookings_by_datevenue[datevenue][slot_label].reservations:
                    reservation.is_playable = True
        data.move_all_playable_players()
        return f"All reservations are set '(playable)'!"
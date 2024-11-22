from auto_registration_system.data_structure.registration_data import RegistrationData


class AllplayableHandler:
    @staticmethod
    def handle(data: RegistrationData) -> str:
        for date_venue in data.bookings_by_date_venue:
            for slot_label in data.bookings_by_date_venue[date_venue]:
                for reservation in data.bookings_by_date_venue[date_venue][slot_label].reservations:
                    reservation.is_playable = True
        data.move_all_playable_players()
        return "Admin has changed all reserve members to (pending)"

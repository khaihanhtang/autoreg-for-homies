from auto_registration_system.data_structure.registration_data import RegistrationData


class AllpendingHandler:
    @staticmethod
    def handle(data: RegistrationData) -> str:
        # Append non-pending reserves after the existing queue, then fill open places.
        for date_venue in data.bookings_by_date_venue:
            for slot_label in data.bookings_by_date_venue[date_venue]:
                slot = data.bookings_by_date_venue[date_venue][slot_label]
                for player_name in data.bookings_by_date_venue[date_venue][slot_label].non_pending_reservations:
                    slot.pending_reservations.append(player_name)
                slot.non_pending_reservations = list()
        data.restructure()
        return "Admin has changed all reserve members to (pending)"

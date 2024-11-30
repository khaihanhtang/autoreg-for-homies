from auto_registration_system.data_structure.registration_data import RegistrationData


class AvHandler:

    @staticmethod
    def handle(data: RegistrationData) -> RegistrationData:
        res = RegistrationData()
        if data is None:
            return res
        for date_venue in data.bookings_by_date_venue:
            slot_container = dict()
            for slot_label, slot in data.bookings_by_date_venue[date_venue].items():
                if len(slot.players) < slot.num_players:
                    slot_container[slot_label] = slot
            if slot_container:
                res.bookings_by_date_venue[date_venue] = slot_container
        return res

from auto_registration_system.data_structure.registration_data import RegistrationData


class AvHandler:

    @staticmethod
    def handle(data: RegistrationData) -> RegistrationData:
        res = RegistrationData()
        if data is None:
            return res
        for datevenue in data.bookings_by_datevenue:
            slot_container = dict()
            for slot_label, slot in data.bookings_by_datevenue[datevenue].items():
                if len(slot.players) < slot.max_num_players:
                    slot_container[slot_label] = slot
            if slot_container:
                res.bookings_by_datevenue[datevenue] = slot_container
        return res

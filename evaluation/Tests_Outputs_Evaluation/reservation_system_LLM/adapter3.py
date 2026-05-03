from reservation_system_LLM.output3 import ReservationSystem as GeneratedSystem


class ReservationSystem:
    
    def __init__(self):
        self.system = GeneratedSystem()

        self.users = set()
        self.rooms = set()
        self.reservations = set()


    def create_user(self, user_id: str):
        self.system.create_user(user_id, user_id)
        self._sync_state()

    def delete_user(self, user_id: str):
        self.system.delete_user(user_id)
        self._sync_state()


    def create_room(self, room_id: str):
        self.system.create_room(room_id, room_id)
        self._sync_state()

    def delete_room(self, room_id: str):
        self.system.delete_room(room_id)
        self._sync_state()


    def create_reservation(self, user_id: str, room_id: str, time=None):
        if time is None:
            start, end = 0, 1
        else:
            start, end = time

        self.system.create_reservation(user_id, room_id, start, end)
        self._sync_state()

    def cancel_reservation(self, user_id: str, room_id: str, time=None):
        if time is None:
            start, end = 0, 1
        else:
            start, end = time

        self.system.cancel_reservation(user_id, room_id, start, end)
        self._sync_state()


    def _sync_state(self):
        self.users = {u.id for u in self.system.get_users()}

        self.rooms = {r.id for r in self.system.get_rooms()}

        new_res = set()

        for r in self.system.get_reservations():
            time = (r.start_time, r.end_time)

            if time == (0, 1):
                time = None

            new_res.add((r.user_id, r.room_id, time))

        self.reservations = new_res

    def get_state(self):
        return {
            "users": self.users,
            "rooms": self.rooms,
            "reservations": self.reservations
        }

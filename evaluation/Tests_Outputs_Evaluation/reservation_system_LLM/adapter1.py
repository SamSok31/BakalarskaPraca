from reservation_system_LLM.output1 import ReservationSystem as GeneratedSystem

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
        for rid, res in list(self.system.reservations.items()):
            if res.user.user_id == user_id and res.room.room_id == room_id:

                if time is None:
                    self.system.cancel_reservation(rid)
                else:
                    if (res.start_time, res.end_time) == time:
                        self.system.cancel_reservation(rid)

        self._sync_state()


    def _sync_state(self):
        self.users = set(self.system.users.keys())

        self.rooms = set(self.system.rooms.keys())

        new_res = set()

        for res in self.system.reservations.values():
            user = res.user.user_id
            room = res.room.room_id

            time = (res.start_time, res.end_time)

            if time == (0, 1):
                time = None

            new_res.add((user, room, time))

        self.reservations = new_res


    def get_state(self):
        return {
            "users": self.users,
            "rooms": self.rooms,
            "reservations": self.reservations,
        }

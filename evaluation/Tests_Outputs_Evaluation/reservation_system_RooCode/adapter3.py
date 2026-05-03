from reservation_system_RooCode.output3 import ReservationSystem as GeneratedSystem
import datetime


class ReservationSystem:

    def __init__(self):
        self.system = GeneratedSystem()

        self.users = set()
        self.rooms = set()
        self.reservations = set()

        self._res_map = {}


    def create_user(self, user_id: str):
        if user_id not in self.users:
            self.system.create_user(user_id, user_id)
            self.users.add(user_id)

    def delete_user(self, user_id: str):
        self.system.delete_user(user_id)
        self.users.discard(user_id)

        self.reservations = {
            r for r in self.reservations if r[0] != user_id
        }
        self._res_map = {
            k: v for k, v in self._res_map.items() if k[0] != user_id
        }


    def create_room(self, room_id: str):
        if room_id not in self.rooms:
            self.system.create_room(room_id, room_id, 1)
            self.rooms.add(room_id)

    def delete_room(self, room_id: str):
        self.system.delete_room(room_id)
        self.rooms.discard(room_id)

        self.reservations = {
            r for r in self.reservations if r[1] != room_id
        }
        self._res_map = {
            k: v for k, v in self._res_map.items() if k[1] != room_id
        }


    def _to_datetime(self, time):
        if time is None:
            return (
                datetime.datetime(2000, 1, 1, 0),
                datetime.datetime(2000, 1, 1, 1)
            )
        return (
            datetime.datetime(2000, 1, 1, time[0]),
            datetime.datetime(2000, 1, 1, time[1])
        )

    def _make_res_id(self, user_id, room_id, time):
        if time is None:
            return f"{user_id}_{room_id}_none"
        return f"{user_id}_{room_id}_{time[0]}_{time[1]}"


    def create_reservation(self, user_id: str, room_id: str, time=None):
        if user_id not in self.users or room_id not in self.rooms:
            return

        key = (user_id, room_id, time)

        if key in self._res_map:
            return

        start, end = self._to_datetime(time)
        res_id = self._make_res_id(user_id, room_id, time)

        success = self.system.create_reservation(
            res_id, user_id, room_id, start, end
        )

        if success:
            self._res_map[key] = res_id
            self.reservations.add(key)

    def cancel_reservation(self, user_id: str, room_id: str, time=None):
        key = (user_id, room_id, time)

        res_id = self._res_map.get(key)
        if not res_id:
            return

        self.system.cancel_reservation(res_id)

        self._res_map.pop(key, None)
        self.reservations.discard(key)


    def get_state(self):
        return {
            "users": self.users,
            "rooms": self.rooms,
            "reservations": self.reservations
        }

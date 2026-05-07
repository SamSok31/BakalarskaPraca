import threading


class ReservationSystem:
    def __init__(self):
        self.users = {}
        self.rooms = {}
        self.reservations = set()
        self.lock = threading.Lock()

    def create_user(self, user_id: str) -> bool:
        if user_id in self.users:
            return False
        self.users[user_id] = None
        return True

    def create_room(self, room_id: str) -> bool:
        if room_id in self.rooms:
            return False
        self.rooms[room_id] = None
        return True

    def delete_user(self, user_id: str) -> bool:
        with self.lock:
            if user_id not in self.users:
                return False

            reservations_to_remove = {r for r in self.reservations if r[1] == user_id}
            self.reservations.difference_update(reservations_to_remove)
            del self.users[user_id]

        return True

    def delete_room(self, room_id: str) -> bool:
        with self.lock:
            if room_id not in self.rooms:
                return False

            reservations_to_remove = {
                (room_id, user_id, start_time, end_time)
                for (r_id, user_id, start_time, end_time) in self.reservations
                if r_id == room_id
            }
            self.reservations.difference_update(reservations_to_remove)
            del self.rooms[room_id]

        return True

    def create_reservation(self, room_id: str, user_id: str, start_time: int, end_time: int) -> bool:
        if user_id not in self.users or room_id not in self.rooms:
            return False

        if not isinstance(start_time, int) or not isinstance(end_time, int) or start_time >= end_time or start_time < 0 or end_time < 0:
            return False

        reservation = (room_id, user_id, start_time, end_time)
        if reservation in self.reservations:
            return True

        for existing_reservation in self.reservations:
            existing_room, existing_user, existing_start, existing_end = existing_reservation
            if existing_room == room_id:
                if not (end_time <= existing_start or start_time >= existing_end):
                    return False

        with self.lock:
            self.reservations.add(reservation)
        return True

    def cancel_reservation(self, room_id: str, user_id: str, start_time: int, end_time: int) -> bool:
        reservation = (room_id, user_id, start_time, end_time)
        if reservation in self.reservations:
            with self.lock:
                self.reservations.remove(reservation)
            return True
        return False

    def get_users(self) -> list[str]:
        return list(self.users.keys())

    def get_rooms(self) -> list[str]:
        return list(self.rooms.keys())

    def get_reservations(self, user_id: str = None, room_id: str = None) -> list[tuple]:
        filtered_reservations = []
        for reservation in self.reservations:
            room_match = room_id is None or reservation[0] == room_id
            user_match = user_id is None or reservation[1] == user_id
            if room_match and user_match:
                filtered_reservations.append(reservation)
        return filtered_reservations
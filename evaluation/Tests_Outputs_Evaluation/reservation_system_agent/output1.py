class ReservationSystem:
    def __init__(self):
        self.users = set()
        self.rooms = set()
        self.reservations = {}

    def create_user(self, user_id):
        if user_id in self.users:
            return False
        self.users.add(user_id)
        return True

    def create_room(self, room_id):
        if room_id in self.rooms:
            return False
        self.rooms.add(room_id)
        return True

    def create_reservation(self, user_id, room_id, start_time, end_time):
        # Check if user and room exist
        if user_id not in self.users or room_id not in self.rooms:
            return False

        # Check if time interval is valid
        if start_time >= end_time:
            return False

        # Check for duplicate reservation
        reservation_key = (user_id, room_id, start_time, end_time)
        if reservation_key in self.reservations:
            return False

        # Check for time conflicts with existing reservations
        for (u_id, r_id, s_time, e_time) in self.reservations.keys():
            if r_id == room_id and not (end_time <= s_time or start_time >= e_time):
                return False

        # Create the reservation
        self.reservations[reservation_key] = None
        return True

    def cancel_reservation(self, user_id, room_id, start_time, end_time):
        reservation_key = (user_id, room_id, start_time, end_time)
        if reservation_key in self.reservations:
            del self.reservations[reservation_key]
            return True
        return False

    def delete_user(self, user_id):
        if user_id not in self.users:
            return False

        self.users.remove(user_id)

        reservations_to_remove = [
            (u, r, s, e) for (u, r, s, e) in self.reservations
            if u == user_id
        ]

        for reservation in reservations_to_remove:
            del self.reservations[reservation]

        return True

    def delete_room(self, room_id):
        if room_id not in self.rooms:
            return False

        self.rooms.remove(room_id)

        reservations_to_remove = [
            (user_id, r_room_id, start_time, end_time)
            for (user_id, r_room_id, start_time, end_time) in self.reservations.keys()
            if r_room_id == room_id
        ]

        for reservation in reservations_to_remove:
            del self.reservations[reservation]

        return True

    def get_users(self):
        """Retrieves the current list of users.

        Returns:
            set: Set of user IDs currently registered in the system.
        """
        return self.users

    def get_rooms(self):
        """Retrieves the current list of rooms.

        Returns:
            set: Set of room IDs currently available in the system.
        """
        return self.rooms

    def get_reservations(self):
        """Retrieves the current list of reservations.

        Returns:
            list: List of active reservations in the system as tuples of
                  (user_id, room_id, start_time, end_time).
        """
        return list(self.reservations.keys())

    def is_room_available(self, room_id: str, start_time: int, end_time: int) -> bool:
        # Check if the room exists
        if room_id not in self.rooms:
            return False

        # Check if time interval is valid
        if start_time >= end_time:
            return False

        # Check for time conflicts with existing reservations
        for (_, res_room_id, res_start, res_end) in self.reservations:
            if res_room_id == room_id:
                # Check for overlap (boundary times are non-overlapping)
                if not (end_time <= res_start or start_time >= res_end):
                    return False

        return True
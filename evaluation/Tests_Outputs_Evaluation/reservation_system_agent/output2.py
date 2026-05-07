import hashlib

class ReservationSystem:
    def __init__(self):
        self.users = {}
        self.rooms = {}
        self.reservations = {}

    def create_user(self, user_id):
        if user_id in self.users:
            return False, "User ID already exists"
        self.users[user_id] = {"user_id": user_id}
        return True, "User created successfully"

    def create_room(self, room_id):
        if room_id in self.rooms:
            return False, f"Room with ID {room_id} already exists."
        self.rooms[room_id] = {"room_id": room_id}
        return True, f"Room with ID {room_id} created successfully."

    def _generate_reservation_id(self, room_id, user_id, time_interval):
        """Generate a consistent reservation ID from room_id, user_id, and time_interval."""
        combined = f"{room_id}_{user_id}_{time_interval[0]}_{time_interval[1]}"
        reservation_id = hashlib.sha256(combined.encode()).hexdigest()
        return reservation_id

    def create_reservation(self, user_id, room_id, time_interval):
        if user_id not in self.users:
            return False, "User does not exist"

        if room_id not in self.rooms:
            return False, "Room does not exist"

        if not isinstance(time_interval, tuple) or len(time_interval) != 2:
            return False, "Invalid time interval format"
        start, end = time_interval
        if not isinstance(start, int) or not isinstance(end, int) or start >= end:
            return False, "Invalid time interval values"

        reservation_id = self._generate_reservation_id(room_id, user_id, time_interval)
        if reservation_id in self.reservations:
            return False, "Reservation already exists"

        for existing_reservation in self.reservations.values():
            if existing_reservation['room_id'] == room_id:
                existing_start, existing_end = existing_reservation['time_interval']
                if not (end <= existing_start or start >= existing_end):
                    return False, "Room is not available for the requested time interval"

        self.reservations[reservation_id] = {
            'room_id': room_id,
            'user_id': user_id,
            'time_interval': time_interval
        }
        return True, "Reservation created successfully"

    def cancel_reservation(self, user_id, room_id, time_interval):
        if not (isinstance(time_interval, tuple) and len(time_interval) == 2 and
                isinstance(time_interval[0], int) and isinstance(time_interval[1], int) and
                time_interval[0] < time_interval[1]):
            return False, "Invalid time interval format. Must be a tuple of two integers where start < end."

        reservation_id = self._generate_reservation_id(room_id, user_id, time_interval)

        if reservation_id in self.reservations:
            reservation = self.reservations[reservation_id]
            if reservation['user_id'] != user_id or reservation['room_id'] != room_id or reservation['time_interval'] != time_interval:
                return False, "Inputs do not match the original reservation's values."
            del self.reservations[reservation_id]
            return True, "Reservation cancelled successfully."
        else:
            return False, "Reservation not found or inputs do not match existing reservation."

    def delete_user(self, user_id):
        reservations_to_remove = [
            res_id for res_id, res in self.reservations.items()
            if res['user_id'] == user_id
        ]
        for res_id in reservations_to_remove:
            del self.reservations[res_id]

        if user_id in self.users:
            del self.users[user_id]
            return True, f"User {user_id} and all associated reservations deleted successfully."
        else:
            if reservations_to_remove:
                return True, f"User {user_id} not found in users dictionary, but associated reservations were deleted."
            else:
                return False, f"User {user_id} not found in users dictionary and no associated reservations exist."

    def delete_room(self, room_id):
        reservations_to_remove = [
            res_id for res_id, res in self.reservations.items()
            if res['room_id'] == room_id
        ]
        for res_id in reservations_to_remove:
            del self.reservations[res_id]

        if room_id in self.rooms:
            del self.rooms[room_id]
            message = f"Room {room_id} and all associated reservations deleted successfully."
            success = True
        else:
            if reservations_to_remove:
                message = f"Room {room_id} not found, but {len(reservations_to_remove)} associated reservations were deleted."
                success = True
            else:
                message = f"Room {room_id} not found and no associated reservations exist."
                success = False

        return success, message

    def get_users(self):
        return [{"user_id": user_id, **user_details} for user_id, user_details in self.users.items()]

    def get_rooms(self):
        return [{"room_id": room_id, **room_details} for room_id, room_details in self.rooms.items()]

    def get_reservations(self):
        reservations_list = []
        for reservation_id, reservation_details in self.reservations.items():
            reservation_dict = {
                'room_id': reservation_details['room_id'],
                'user_id': reservation_details['user_id'],
                'time_interval': reservation_details['time_interval']
            }
            reservations_list.append(reservation_dict)
        return reservations_list
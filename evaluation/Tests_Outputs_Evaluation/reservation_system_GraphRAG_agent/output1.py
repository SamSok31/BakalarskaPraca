class ReservationSystem:
    def __init__(self):
        self.users = set()
        self.rooms = set()
        self.reservations = []

    def create_user(self, user_id):
        if user_id in self.users:
            return False, f"User {user_id} already exists"
        self.users.add(user_id)
        return True, f"User {user_id} created successfully"

    def create_room(self, room_id):
        if room_id in self.rooms:
            return False, "Room already exists"
        self.rooms.add(room_id)
        return True, "Room created successfully"

    def cancel_reservation(self, user_id, room_id, start_time, end_time):
        # Check if the reservation exists
        reservation_to_cancel = {
            'user_id': user_id,
            'room_id': room_id,
            'start_time': start_time,
            'end_time': end_time
        }

        # Find the reservation in the list
        for reservation in self.reservations:
            if (reservation['user_id'] == user_id and
                reservation['room_id'] == room_id and
                reservation['start_time'] == start_time and
                reservation['end_time'] == end_time):
                self.reservations.remove(reservation)
                return True, "Reservation cancelled successfully"

        return False, "Reservation not found"

    def delete_user(self, user_id):
        if user_id not in self.users:
            return False, f"User {user_id} does not exist in the system."

        # Count reservations before removal
        num_reservations_removed = len([r for r in self.reservations if r['user_id'] == user_id])

        # Remove all reservations associated with the user
        self.reservations = [r for r in self.reservations if r['user_id'] != user_id]

        # Remove the user from the system
        self.users.remove(user_id)

        return True, f"User {user_id} and {num_reservations_removed} associated reservations have been successfully deleted."

    def delete_room(self, room_id):
        if room_id not in self.rooms:
            return False, f"Room {room_id} does not exist in the system."

        # Count reservations before removal
        num_reservations_removed = len([r for r in self.reservations if r['room_id'] == room_id])

        # Remove all reservations associated with the room
        self.reservations = [
            res for res in self.reservations
            if res['room_id'] != room_id
        ]

        # Remove the room from the system
        self.rooms.remove(room_id)

        return True, f"Room {room_id} and {num_reservations_removed} associated reservations have been successfully deleted."

    def create_reservation(self, user_id, room_id, start_time, end_time):
        # Check if user and room exist
        if user_id not in self.users:
            return False, "User does not exist"
        if room_id not in self.rooms:
            return False, "Room does not exist"

        # Validate time interval
        if start_time >= end_time:
            return False, "Invalid time interval: start_time must be less than end_time"

        # Check for time conflicts
        for reservation in self.reservations:
            if reservation['room_id'] == room_id:
                # Check for overlapping or boundary time conflicts
                if not (end_time <= reservation['start_time'] or start_time >= reservation['end_time']):
                    return False, "Time conflict with existing reservation (including boundary times)"

        # Create the reservation
        new_reservation = {
            'user_id': user_id,
            'room_id': room_id,
            'start_time': start_time,
            'end_time': end_time
        }
        self.reservations.append(new_reservation)
        return True, "Reservation created successfully"

    def get_system_state(self, user_id=None, room_id=None, start_time=None, end_time=None):
        # Get all users and rooms
        users = self.users.copy()
        rooms = self.rooms.copy()

        # Filter reservations based on provided parameters
        filtered_reservations = []
        for reservation in self.reservations:
            # Check user_id filter
            if user_id is not None and reservation['user_id'] != user_id:
                continue

            # Check room_id filter
            if room_id is not None and reservation['room_id'] != room_id:
                continue

            # Check time interval filter
            if start_time is not None and end_time is not None:
                # Check for overlapping intervals (boundary handling)
                if not (reservation['end_time'] <= start_time or reservation['start_time'] >= end_time):
                    filtered_reservations.append(reservation)
            else:
                filtered_reservations.append(reservation)

        return users, rooms, filtered_reservations
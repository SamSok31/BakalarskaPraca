from datetime import datetime

class ReservationSystem:
    def __init__(self):
        self.users = {}
        self.rooms = {}
        self.reservations = {}
        self.cancelled_reservations = set()
        self.reservation_id_counter = 1

    def create_user(self, user_id):
        if user_id in self.users:
            return False
        self.users[user_id] = {}
        return True

    def create_room(self, room_id):
        if room_id in self.rooms:
            return False
        self.rooms[room_id] = {}
        return True

    def get_users(self):
        """Retrieve the current state of all users.

        Returns:
            dict: Dictionary of all users with their IDs as keys.
        """
        return self.users

    def get_rooms(self):
        """Retrieve the current state of all rooms.

        Returns:
            dict: Dictionary of all rooms with their IDs as keys.
        """
        return self.rooms

    def create_reservation(self, room_id, user_id, start_time, end_time):
        # Check if user and room exist
        if user_id not in self.users or room_id not in self.rooms:
            return False, "User or room does not exist"

        # Validate time interval
        if start_time >= end_time:
            return False, "Start time must be before end time"

        # Check for existing active reservation
        for reservation in self.reservations.values():
            if (reservation['room_id'] == room_id and
                reservation['user_id'] == user_id and
                reservation['start_time'] == start_time and
                reservation['end_time'] == end_time):
                return False, "Reservation already exists"

        # Check for previously cancelled reservation
        cancelled_key = (room_id, user_id, start_time, end_time)
        if cancelled_key in self.cancelled_reservations:
            self.cancelled_reservations.remove(cancelled_key)
            message = "Previously cancelled reservation recreated successfully"
        else:
            message = "Reservation created successfully"

        # Check for overlapping reservations
        for reservation in self.reservations.values():
            if reservation['room_id'] == room_id:
                # Check for overlapping time intervals (boundary times are non-overlapping)
                if not (end_time <= reservation['start_time'] or start_time >= reservation['end_time']):
                    return False, "Room is already reserved for the requested time interval"

        # Create new reservation
        reservation_id = self.reservation_id_counter
        self.reservations[reservation_id] = {
            'room_id': room_id,
            'user_id': user_id,
            'start_time': start_time,
            'end_time': end_time
        }
        self.reservation_id_counter += 1

        return True, message

    def cancel_reservation(self, room_id, user_id, start_time, end_time):
        # Check if the reservation exists in the reservations dictionary
        for reservation_id, reservation in self.reservations.items():
            if (reservation['room_id'] == room_id and
                reservation['user_id'] == user_id and
                reservation['start_time'] == start_time and
                reservation['end_time'] == end_time):
                # Remove the reservation from active reservations
                del self.reservations[reservation_id]
                # Add the reservation details to cancelled_reservations
                self.cancelled_reservations.add((room_id, user_id, start_time, end_time))
                return True
        return False

    def delete_user(self, user_id):
        if user_id not in self.users:
            return False

        del self.users[user_id]

        # Collect all reservation IDs to cancel
        reservations_to_cancel = []
        for reservation_id, reservation in self.reservations.items():
            if reservation['user_id'] == user_id:
                reservations_to_cancel.append(reservation_id)

        # Cancel all reservations
        for reservation_id in reservations_to_cancel:
            reservation = self.reservations[reservation_id]
            room_id = reservation['room_id']
            start_time = reservation['start_time']
            end_time = reservation['end_time']
            # Remove from cancelled_reservations if it exists
            cancelled_key = (room_id, user_id, start_time, end_time)
            if cancelled_key in self.cancelled_reservations:
                self.cancelled_reservations.remove(cancelled_key)
            # Use cancel_reservation method to properly handle the cancellation
            self.cancel_reservation(room_id, user_id, start_time, end_time)

        return True

    def delete_room(self, room_id):
        if room_id not in self.rooms:
            return False

        # Remove the room from the rooms dictionary
        del self.rooms[room_id]

        # Collect all reservation IDs to cancel
        reservations_to_cancel = []
        for reservation_id, reservation in self.reservations.items():
            if reservation['room_id'] == room_id:
                reservations_to_cancel.append(reservation_id)

        # Cancel all reservations
        for reservation_id in reservations_to_cancel:
            reservation = self.reservations[reservation_id]
            # Remove the reservation from cancelled_reservations if it exists
            cancelled_key = (reservation['room_id'], reservation['user_id'], reservation['start_time'], reservation['end_time'])
            if cancelled_key in self.cancelled_reservations:
                self.cancelled_reservations.remove(cancelled_key)
            # Cancel the reservation using the existing cancel_reservation method
            self.cancel_reservation(
                reservation['room_id'],
                reservation['user_id'],
                reservation['start_time'],
                reservation['end_time']
            )

        return True

    def get_reservations(self, user_id=None, room_id=None, start_time=None, end_time=None):
        result = {}
        for reservation_id, reservation in self.reservations.items():
            # Check user_id filter
            if user_id is not None and reservation['user_id'] != user_id:
                continue
            # Check room_id filter
            if room_id is not None and reservation['room_id'] != room_id:
                continue
            # Check time interval filter
            if start_time is not None or end_time is not None:
                res_start = reservation['start_time']
                res_end = reservation['end_time']
                # Check for non-overlapping (with boundary times considered non-overlapping)
                if (start_time is not None and res_end <= start_time) or (end_time is not None and res_start >= end_time):
                    continue
            result[reservation_id] = reservation
        return result
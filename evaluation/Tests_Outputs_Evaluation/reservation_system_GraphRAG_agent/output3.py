import threading
import uuid


class ReservationSystem:
    def __init__(self):
        self.users = {}
        self.rooms = {}
        self.reservations = {}
        self._lock = threading.Lock()

    def create_user(self, user_id):
        with self._lock:
            if user_id in self.users:
                return False
            self.users[user_id] = {'user_id': user_id}
            return True

    def create_room(self, room_id):
        with self._lock:
            if room_id in self.rooms:
                return False
            self.rooms[room_id] = {'room_id': room_id}
            return True

    def delete_user(self, user_id):
        with self._lock:
            if user_id not in self.users:
                return False

            # Remove all reservations associated with the user
            reservations_to_remove = [
                res_id for res_id, res in self.reservations.items()
                if res['user_id'] == user_id
            ]
            for res_id in reservations_to_remove:
                del self.reservations[res_id]

            # Remove the user
            del self.users[user_id]

            return True

    def delete_room(self, room_id):
        with self._lock:
            if room_id not in self.rooms:
                return False

            # Remove all reservations associated with the room
            reservations_to_remove = [
                res_id for res_id, res in self.reservations.items()
                if res['room_id'] == room_id
            ]
            for res_id in reservations_to_remove:
                del self.reservations[res_id]

            # Remove the room
            del self.rooms[room_id]
            return True

    def create_reservation(self, user_id, room_id, start_time, end_time):
        with self._lock:
            # Check if user and room exist
            if user_id not in self.users or room_id not in self.rooms:
                return False

            # Validate time range
            if end_time <= start_time:
                return False

            # Check for time conflicts and duplicates in one pass
            for reservation in self.reservations.values():
                if reservation['room_id'] == room_id:
                    # Check for overlapping time ranges (boundary times are non-overlapping)
                    if not (end_time <= reservation['start_time'] or start_time >= reservation['end_time']):
                        return False
                    # Check for duplicate reservation
                    if (reservation['user_id'] == user_id and
                        reservation['start_time'] == start_time and
                        reservation['end_time'] == end_time):
                        return False

            # Generate unique reservation_id
            reservation_id = str(uuid.uuid4())

            # Create reservation
            self.reservations[reservation_id] = {
                'user_id': user_id,
                'room_id': room_id,
                'start_time': start_time,
                'end_time': end_time,
                'reservation_id': reservation_id
            }

            return True

    def cancel_reservation(self, reservation_id):
        with self._lock:
            if reservation_id in self.reservations:
                del self.reservations[reservation_id]
                return True
            return False

    def get_users(self, filters=None, sort_by=None):
        with self._lock:
            if filters is None:
                filters = {}
            if sort_by is None:
                sort_by = 'user_id'

            users = list(self.users.values())

            # Apply filters
            if filters:
                filtered_users = []
                for user in users:
                    match = True
                    for key, value in filters.items():
                        if key not in user or user[key] != value:
                            match = False
                            break
                    if match:
                        filtered_users.append(user)
                users = filtered_users

            # Sort results
            try:
                users.sort(key=lambda x: x[sort_by])
            except KeyError:
                # Default to sorting by user_id if sort_by is invalid
                users.sort(key=lambda x: x['user_id'])

            return users

    def get_rooms(self, filters=None, sort_by=None):
        with self._lock:
            if filters is None:
                filters = {}
            if sort_by is None:
                sort_by = 'room_id'

            rooms = list(self.rooms.values())

            # Apply filters
            if filters:
                filtered_rooms = []
                for room in rooms:
                    match = True
                    for key, value in filters.items():
                        if key not in room or room[key] != value:
                            match = False
                            break
                    if match:
                        filtered_rooms.append(room)
                rooms = filtered_rooms

            # Sort results
            try:
                rooms.sort(key=lambda x: x[sort_by])
            except KeyError:
                # Default to sorting by room_id if sort_by is invalid
                rooms.sort(key=lambda x: x['room_id'])

            return rooms

    def get_reservations(self, filters=None, sort_by=None):
        with self._lock:
            if filters is None:
                filters = {}
            if sort_by is None:
                sort_by = 'start_time'

            reservations = list(self.reservations.values())

            # Apply filters in a single pass
            filtered_reservations = []
            for reservation in reservations:
                match = True

                # User ID filter
                if 'user_id' in filters and reservation['user_id'] != filters['user_id']:
                    match = False

                # Room ID filter
                if 'room_id' in filters and reservation['room_id'] != filters['room_id']:
                    match = False

                # Time range filter (non-overlapping boundaries)
                if 'start_time' in filters and 'end_time' in filters:
                    filter_start = filters['start_time']
                    filter_end = filters['end_time']
                    if not (reservation['end_time'] <= filter_start or reservation['start_time'] >= filter_end):
                        match = False

                if match:
                    filtered_reservations.append(reservation)

            # Sort results
            valid_sort_fields = {'user_id', 'room_id', 'start_time', 'end_time', 'reservation_id'}
            if sort_by in valid_sort_fields:
                filtered_reservations.sort(key=lambda x: x[sort_by])
            else:
                filtered_reservations.sort(key=lambda x: x['start_time'])

            return filtered_reservations
class User:
    def __init__(self, user_id, name):
        self.user_id = user_id
        self.name = name

    def __repr__(self):
        return f"User(ID: {self.user_id}, Name: {self.name})"


class Room:
    def __init__(self, room_id, name):
        self.room_id = room_id
        self.name = name

    def __repr__(self):
        return f"Room(ID: {self.room_id}, Name: {self.name})"


class Reservation:
    def __init__(self, reservation_id, user, room, start_time, end_time):
        self.reservation_id = reservation_id
        self.user = user
        self.room = room
        self.start_time = start_time
        self.end_time = end_time

    def overlaps_with(self, other):
        return (self.start_time < other.end_time and self.end_time > other.start_time)

    def __repr__(self):
        return (f"Reservation(ID: {self.reservation_id}, User: {self.user.user_id}, "
                f"Room: {self.room.room_id}, Time: {self.start_time} to {self.end_time})"
               )


class ReservationSystem:
    def __init__(self):
        self.users = {}
        self.rooms = {}
        self.reservations = {}
        self.next_reservation_id = 1

    def create_user(self, user_id, name):
        if user_id not in self.users:
            self.users[user_id] = User(user_id, name)

    def delete_user(self, user_id):
        if user_id in self.users:
            # Remove all reservations associated with the user
            to_remove = [rid for rid, res in self.reservations.items() if res.user.user_id == user_id]
            for rid in to_remove:
                del self.reservations[rid]
            del self.users[user_id]

    def create_room(self, room_id, name):
        if room_id not in self.rooms:
            self.rooms[room_id] = Room(room_id, name)

    def delete_room(self, room_id):
        if room_id in self.rooms:
            # Remove all reservations associated with the room
            to_remove = [rid for rid, res in self.reservations.items() if res.room.room_id == room_id]
            for rid in to_remove:
                del self.reservations[rid]
            del self.rooms[room_id]

    def create_reservation(self, user_id, room_id, start_time, end_time):
        if user_id not in self.users or room_id not in self.rooms:
            return None

        user = self.users[user_id]
        room = self.rooms[room_id]

        # Check for overlapping reservations
        for res in self.reservations.values():
            if res.room.room_id == room_id and res.overlaps_with(Reservation(None, None, None, start_time, end_time)):
                return None

        reservation = Reservation(self.next_reservation_id, user, room, start_time, end_time)
        self.reservations[self.next_reservation_id] = reservation
        self.next_reservation_id += 1
        return reservation

    def cancel_reservation(self, reservation_id):
        if reservation_id in self.reservations:
            del self.reservations[reservation_id]

    def get_reservations(self):
        return list(self.reservations.values())

    def get_users(self):
        return list(self.users.values())

    def get_rooms(self):
        return list(self.rooms.values())
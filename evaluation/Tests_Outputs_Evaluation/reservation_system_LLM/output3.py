from dataclasses import dataclass
from typing import Dict, List, Optional

@dataclass
class User:
    id: str
    name: str

@dataclass
class Room:
    id: str
    name: str

@dataclass
class Reservation:
    user_id: str
    room_id: str
    start_time: int
    end_time: int

class ReservationSystem:
    def __init__(self):
        self.users: Dict[str, User] = {}
        self.rooms: Dict[str, Room] = {}
        self.reservations: List[Reservation] = []

    def create_user(self, id: str, name: str) -> None:
        if id not in self.users:
            self.users[id] = User(id, name)

    def delete_user(self, id: str) -> None:
        if id in self.users:
            del self.users[id]
            self.reservations = [r for r in self.reservations if r.user_id != id]

    def create_room(self, id: str, name: str) -> None:
        if id not in self.rooms:
            self.rooms[id] = Room(id, name)

    def delete_room(self, id: str) -> None:
        if id in self.rooms:
            del self.rooms[id]
            self.reservations = [r for r in self.reservations if r.room_id != id]

    def create_reservation(self, user_id: str, room_id: str, start_time: int, end_time: int) -> bool:
        if user_id not in self.users or room_id not in self.rooms:
            return False

        for r in self.reservations:
            if r.room_id == room_id and not (end_time <= r.start_time or start_time >= r.end_time):
                return False

        self.reservations.append(Reservation(user_id, room_id, start_time, end_time))
        return True

    def cancel_reservation(self, user_id: str, room_id: str, start_time: int, end_time: int) -> bool:
        for i, r in enumerate(self.reservations):
            if r.user_id == user_id and r.room_id == room_id and r.start_time == start_time and r.end_time == end_time:
                self.reservations.pop(i)
                return True
        return False

    def get_users(self) -> List[User]:
        return list(self.users.values())

    def get_rooms(self) -> List[Room]:
        return list(self.rooms.values())

    def get_reservations(self) -> List[Reservation]:
        return self.reservations
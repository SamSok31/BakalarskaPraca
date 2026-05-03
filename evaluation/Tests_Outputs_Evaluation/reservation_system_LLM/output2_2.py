from dataclasses import dataclass
from typing import Dict, List, Optional

@dataclass
class User:
    user_id: str

@dataclass
class Room:
    room_id: str

@dataclass
class Reservation:
    user_id: str
    room_id: str
    start_time: int  # Using Unix timestamp for simplicity
    end_time: int

class ReservationSystem:
    def __init__(self):
        self.users: Dict[str, User] = {}
        self.rooms: Dict[str, Room] = {}
        self.reservations: List[Reservation] = []

    def create_user(self, user_id: str) -> None:
        if user_id not in self.users:
            self.users[user_id] = User(user_id)

    def create_room(self, room_id: str) -> None:
        if room_id not in self.rooms:
            self.rooms[room_id] = Room(room_id)

    def delete_user(self, user_id: str) -> None:
        if user_id in self.users:
            del self.users[user_id]
            self.reservations = [
                r for r in self.reservations if r.user_id != user_id
            ]

    def delete_room(self, room_id: str) -> None:
        if room_id in self.rooms:
            del self.rooms[room_id]
            self.reservations = [
                r for r in self.reservations if r.room_id != room_id
            ]

    def create_reservation(
        self, user_id: str, room_id: str, start_time: int, end_time: int
    ) -> bool:
        if (
            user_id not in self.users
            or room_id not in self.rooms
            or start_time >= end_time
        ):
            return False

        for r in self.reservations:
            if r.room_id == room_id:
                if not (
                    end_time <= r.start_time
                    or start_time >= r.end_time
                ):
                    return False

        self.reservations.append(
            Reservation(user_id, room_id, start_time, end_time)
        )
        return True

    def cancel_reservation(
        self, user_id: str, room_id: str, start_time: int, end_time: int
    ) -> bool:
        for i, r in enumerate(self.reservations):
            if (
                r.user_id == user_id
                and r.room_id == room_id
                and r.start_time == start_time
                and r.end_time == end_time
            ):
                self.reservations.pop(i)
                return True
        return False

    def get_reservations(self) -> List[Reservation]:
        return self.reservations

    def get_users(self) -> Dict[str, User]:
        return self.users

    def get_rooms(self) -> Dict[str, Room]:
        return self.rooms
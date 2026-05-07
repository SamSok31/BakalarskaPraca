#!/usr/bin/env python3
"""
Reservation System in Python

This system manages reservations for rooms by users. Each room can only be reserved by one user at a time.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Set


@dataclass
class User:
    """Represents a user in the reservation system."""
    user_id: str


@dataclass
class Room:
    """Represents a room in the reservation system."""
    room_id: str


@dataclass
class Reservation:
    """Represents a reservation in the system."""
    reservation_id: str
    user_id: str
    room_id: str
    start_time: int  # Using integer to represent time slots
    end_time: int    # Using integer to represent time slots


class ReservationSystem:
    """Core reservation system managing users, rooms, and reservations."""

    def __init__(self) -> None:
        """Initialize the reservation system."""
        self.users: Dict[str, User] = {}
        self.rooms: Dict[str, Room] = {}
        self.reservations: Dict[str, Reservation] = {}
        self.room_reservations: Dict[str, Dict[str, Reservation]] = {}  # room_id -> {reservation_id -> Reservation}
        self.user_reservations: Dict[str, Dict[str, Reservation]] = {}  # user_id -> {reservation_id -> Reservation}

    def create_user(self, user_id: str) -> None:
        """Create a new user with the given ID.
        
        If a user with the same ID already exists, no effect.
        """
        if user_id not in self.users:
            self.users[user_id] = User(user_id=user_id)
            self.user_reservations[user_id] = {}

    def delete_user(self, user_id: str) -> None:
        """Delete a user with the given ID.
        
        Removes all reservations associated with this user.
        If the user does not exist, no effect.
        """
        if user_id in self.users:
            # Remove all reservations for this user
            if user_id in self.user_reservations:
                for reservation_id in list(self.user_reservations[user_id].keys()):
                    self._cancel_reservation(reservation_id)
                del self.user_reservations[user_id]
            del self.users[user_id]

    def create_room(self, room_id: str) -> None:
        """Create a new room with the given ID.
        
        If a room with the same ID already exists, no effect.
        """
        if room_id not in self.rooms:
            self.rooms[room_id] = Room(room_id=room_id)
            self.room_reservations[room_id] = {}

    def delete_room(self, room_id: str) -> None:
        """Delete a room with the given ID.
        
        Removes all reservations associated with this room.
        If the room does not exist, no effect.
        """
        if room_id in self.rooms:
            # Remove all reservations for this room
            if room_id in self.room_reservations:
                for reservation_id in list(self.room_reservations[room_id].keys()):
                    self._cancel_reservation(reservation_id)
                del self.room_reservations[room_id]
            del self.rooms[room_id]

    def create_reservation(self, reservation_id: str, user_id: str, room_id: str, start_time: int, end_time: int) -> bool:
        """Create a new reservation if no conflict exists.
        
        Args:
            reservation_id: Unique identifier for the reservation
            user_id: ID of the user making the reservation
            room_id: ID of the room to reserve
            start_time: Start time of the reservation
            end_time: End time of the reservation
            
        Returns:
            bool: True if reservation was created, False if conflict or invalid
            
        Notes:
            - Reservation only succeeds if both user and room exist
            - Reservation only succeeds if no time conflict with existing reservations
            - Boundary times are considered non-overlapping (e.g., [10,11] and [11,12])
        """
        # Check if user and room exist
        if user_id not in self.users or room_id not in self.rooms:
            return False
            
        # Check if reservation with this ID already exists
        if reservation_id in self.reservations:
            return False
            
        # Check for time conflicts
        if self._has_time_conflict(room_id, start_time, end_time):
            return False
            
        # Create the reservation
        reservation = Reservation(
            reservation_id=reservation_id,
            user_id=user_id,
            room_id=room_id,
            start_time=start_time,
            end_time=end_time
        )
        
        self.reservations[reservation_id] = reservation
        self.room_reservations[room_id][reservation_id] = reservation
        self.user_reservations[user_id][reservation_id] = reservation
        
        return True

    def cancel_reservation(self, reservation_id: str) -> None:
        """Cancel an existing reservation.
        
        If the reservation does not exist, no effect.
        """
        self._cancel_reservation(reservation_id)

    def _cancel_reservation(self, reservation_id: str) -> None:
        """Internal method to cancel a reservation."""
        if reservation_id in self.reservations:
            reservation = self.reservations[reservation_id]
            
            # Remove from room_reservations
            if reservation.room_id in self.room_reservations and reservation_id in self.room_reservations[reservation.room_id]:
                del self.room_reservations[reservation.room_id][reservation_id]
            
            # Remove from user_reservations
            if reservation.user_id in self.user_reservations and reservation_id in self.user_reservations[reservation.user_id]:
                del self.user_reservations[reservation.user_id][reservation_id]
            
            # Remove from main reservations
            del self.reservations[reservation_id]

    def _has_time_conflict(self, room_id: str, start_time: int, end_time: int) -> bool:
        """Check if there's a time conflict for a room reservation.
        
        Args:
            room_id: ID of the room to check
            start_time: Proposed start time
            end_time: Proposed end time
            
        Returns:
            bool: True if conflict exists, False otherwise
        """
        if room_id not in self.room_reservations:
            return False
            
        for reservation in self.room_reservations[room_id].values():
            # Check if time intervals overlap
            # Overlap occurs if: existing_start < proposed_end AND existing_end > proposed_start
            if reservation.start_time < end_time and reservation.end_time > start_time:
                return True
        
        return False

    def get_users(self) -> List[User]:
        """Get a list of all users."""
        return list(self.users.values())

    def get_rooms(self) -> List[Room]:
        """Get a list of all rooms."""
        return list(self.rooms.values())

    def get_reservations(self) -> List[Reservation]:
        """Get a list of all reservations."""
        return list(self.reservations.values())

    def get_user_reservations(self, user_id: str) -> List[Reservation]:
        """Get all reservations for a specific user."""
        if user_id in self.user_reservations:
            return list(self.user_reservations[user_id].values())
        return []

    def get_room_reservations(self, room_id: str) -> List[Reservation]:
        """Get all reservations for a specific room."""
        if room_id in self.room_reservations:
            return list(self.room_reservations[room_id].values())
        return []

    def get_reservation(self, reservation_id: str) -> Optional[Reservation]:
        """Get a specific reservation by ID."""
        return self.reservations.get(reservation_id)

    def clear_all(self) -> None:
        """Clear all data in the system (for testing purposes)."""
        self.users.clear()
        self.rooms.clear()
        self.reservations.clear()
        self.room_reservations.clear()
        self.user_reservations.clear()
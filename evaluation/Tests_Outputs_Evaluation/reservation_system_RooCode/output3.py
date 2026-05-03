#!/usr/bin/env python3
"""
Reservation System Implementation

This module provides a reservation system for managing room reservations by users.
The system ensures that:
- Each room can only be reserved by one user at a time (no double booking)
- Multiple reservations for different rooms by the same user are allowed
- Users and rooms can be created and deleted
- Reservations can be created and cancelled
- The system maintains internal consistency
"""

from __future__ import annotations
from typing import Dict, List, Optional, Set
from dataclasses import dataclass
import datetime


@dataclass(frozen=True)
class TimeInterval:
    """Represents a time interval for reservations."""
    start: datetime.datetime
    end: datetime.datetime

    def __post_init__(self):
        if self.start >= self.end:
            raise ValueError("Start time must be before end time")

    def overlaps(self, other: TimeInterval) -> bool:
        """Check if this time interval overlaps with another."""
        return not (self.end <= other.start or other.end <= self.start)


@dataclass(frozen=True)
class User:
    """Represents a user in the reservation system."""
    user_id: str
    name: str


@dataclass(frozen=True)
class Room:
    """Represents a room in the reservation system."""
    room_id: str
    name: str
    capacity: int


@dataclass(frozen=True)
class Reservation:
    """Represents a reservation in the system."""
    reservation_id: str
    user_id: str
    room_id: str
    time_interval: TimeInterval


class ReservationSystem:
    """Main reservation system class that manages users, rooms, and reservations."""

    def __init__(self):
        self.users: Dict[str, User] = {}
        self.rooms: Dict[str, Room] = {}
        self.reservations: Dict[str, Reservation] = {}
        self.reservations_by_room: Dict[str, Dict[str, Reservation]] = {}  # room_id -> {reservation_id -> Reservation}
        self.reservations_by_user: Dict[str, Dict[str, Reservation]] = {}  # user_id -> {reservation_id -> Reservation}

    def create_user(self, user_id: str, name: str) -> bool:
        """
        Create a new user in the system.
        
        Args:
            user_id: Unique identifier for the user
            name: Name of the user
            
        Returns:
            bool: True if user was created, False if user already exists
        """
        if user_id in self.users:
            return False
        
        self.users[user_id] = User(user_id=user_id, name=name)
        self.reservations_by_user[user_id] = {}
        return True

    def delete_user(self, user_id: str) -> bool:
        """
        Delete a user from the system.
        
        Args:
            user_id: ID of the user to delete
            
        Returns:
            bool: True if user was deleted, False if user didn't exist
        """
        if user_id not in self.users:
            return False

        # Remove all reservations associated with this user
        if user_id in self.reservations_by_user:
            reservation_ids = list(self.reservations_by_user[user_id].keys())
            for reservation_id in reservation_ids:
                self._cancel_reservation_internal(reservation_id)
            del self.reservations_by_user[user_id]

        del self.users[user_id]
        return True

    def create_room(self, room_id: str, name: str, capacity: int) -> bool:
        """
        Create a new room in the system.
        
        Args:
            room_id: Unique identifier for the room
            name: Name of the room
            capacity: Capacity of the room
            
        Returns:
            bool: True if room was created, False if room already exists
        """
        if room_id in self.rooms:
            return False
        
        self.rooms[room_id] = Room(room_id=room_id, name=name, capacity=capacity)
        self.reservations_by_room[room_id] = {}
        return True

    def delete_room(self, room_id: str) -> bool:
        """
        Delete a room from the system.
        
        Args:
            room_id: ID of the room to delete
            
        Returns:
            bool: True if room was deleted, False if room didn't exist
        """
        if room_id not in self.rooms:
            return False

        # Remove all reservations associated with this room
        if room_id in self.reservations_by_room:
            reservation_ids = list(self.reservations_by_room[room_id].keys())
            for reservation_id in reservation_ids:
                self._cancel_reservation_internal(reservation_id)
            del self.reservations_by_room[room_id]

        del self.rooms[room_id]
        return True

    def create_reservation(
        self, 
        reservation_id: str, 
        user_id: str, 
        room_id: str, 
        start: datetime.datetime, 
        end: datetime.datetime
    ) -> bool:
        """
        Create a new reservation in the system.
        
        Args:
            reservation_id: Unique identifier for the reservation
            user_id: ID of the user making the reservation
            room_id: ID of the room being reserved
            start: Start time of the reservation
            end: End time of the reservation
            
        Returns:
            bool: True if reservation was created, False if reservation failed
        """
        # Check if reservation already exists
        if reservation_id in self.reservations:
            return False

        # Check if user and room exist
        if user_id not in self.users or room_id not in self.rooms:
            return False

        # Create time interval
        try:
            time_interval = TimeInterval(start=start, end=end)
        except ValueError:
            return False

        # Check for conflicts with existing reservations for this room
        if room_id in self.reservations_by_room:
            for existing_reservation in self.reservations_by_room[room_id].values():
                if existing_reservation.time_interval.overlaps(time_interval):
                    return False  # Conflict found

        # Create the reservation
        reservation = Reservation(
            reservation_id=reservation_id,
            user_id=user_id,
            room_id=room_id,
            time_interval=time_interval
        )

        # Add to main reservations dict
        self.reservations[reservation_id] = reservation
        
        # Add to room index
        if room_id not in self.reservations_by_room:
            self.reservations_by_room[room_id] = {}
        self.reservations_by_room[room_id][reservation_id] = reservation
        
        # Add to user index
        if user_id not in self.reservations_by_user:
            self.reservations_by_user[user_id] = {}
        self.reservations_by_user[user_id][reservation_id] = reservation
        
        return True

    def cancel_reservation(self, reservation_id: str) -> bool:
        """
        Cancel an existing reservation.
        
        Args:
            reservation_id: ID of the reservation to cancel
            
        Returns:
            bool: True if reservation was cancelled, False if reservation didn't exist
        """
        return self._cancel_reservation_internal(reservation_id)

    def _cancel_reservation_internal(self, reservation_id: str) -> bool:
        """Internal method to cancel a reservation and clean up indexes."""
        if reservation_id not in self.reservations:
            return False

        reservation = self.reservations[reservation_id]
        
        # Remove from main reservations
        del self.reservations[reservation_id]
        
        # Remove from room index
        if reservation.room_id in self.reservations_by_room:
            if reservation_id in self.reservations_by_room[reservation.room_id]:
                del self.reservations_by_room[reservation.room_id][reservation_id]
        
        # Remove from user index
        if reservation.user_id in self.reservations_by_user:
            if reservation_id in self.reservations_by_user[reservation.user_id]:
                del self.reservations_by_user[reservation.user_id][reservation_id]
        
        return True

    def get_users(self) -> List[User]:
        """Get a list of all users in the system."""
        return list(self.users.values())

    def get_rooms(self) -> List[Room]:
        """Get a list of all rooms in the system."""
        return list(self.rooms.values())

    def get_reservations(self) -> List[Reservation]:
        """Get a list of all reservations in the system."""
        return list(self.reservations.values())

    def get_user_reservations(self, user_id: str) -> List[Reservation]:
        """Get all reservations for a specific user."""
        if user_id not in self.reservations_by_user:
            return []
        return list(self.reservations_by_user[user_id].values())

    def get_room_reservations(self, room_id: str) -> List[Reservation]:
        """Get all reservations for a specific room."""
        if room_id not in self.reservations_by_room:
            return []
        return list(self.reservations_by_room[room_id].values())

    def get_user(self, user_id: str) -> Optional[User]:
        """Get a specific user by ID."""
        return self.users.get(user_id)

    def get_room(self, room_id: str) -> Optional[Room]:
        """Get a specific room by ID."""
        return self.rooms.get(room_id)

    def get_reservation(self, reservation_id: str) -> Optional[Reservation]:
        """Get a specific reservation by ID."""
        return self.reservations.get(reservation_id)

    def is_room_available(
        self, 
        room_id: str, 
        start: datetime.datetime, 
        end: datetime.datetime
    ) -> bool:
        """
        Check if a room is available for a given time interval.
        
        Args:
            room_id: ID of the room to check
            start: Start time of the interval
            end: End time of the interval
            
        Returns:
            bool: True if the room is available, False otherwise
        """
        if room_id not in self.rooms:
            return False

        try:
            time_interval = TimeInterval(start=start, end=end)
        except ValueError:
            return False

        if room_id not in self.reservations_by_room:
            return True

        for reservation in self.reservations_by_room[room_id].values():
            if reservation.time_interval.overlaps(time_interval):
                return False

        return True
#!/usr/bin/env python3
"""
Reservation System Implementation

This module provides a reservation system for managing room bookings by users.
The system ensures that:
- Each room can only be reserved by one user at a time
- Multiple bookings of different rooms for the same user are allowed
- The system maintains internal consistency
- All operations are conflict-free and handle edge cases appropriately
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Set, Tuple
import time


@dataclass(frozen=True)
class TimeInterval:
    """Represents a time interval for reservations."""
    start_time: int  # Unix timestamp
    end_time: int    # Unix timestamp
    
    def __post_init__(self):
        """Validate that start_time is before end_time."""
        if self.start_time >= self.end_time:
            raise ValueError("start_time must be before end_time")
    
    def overlaps(self, other: 'TimeInterval') -> bool:
        """Check if this time interval overlaps with another.
        
        Boundary times are considered non-overlapping (e.g., [10,11] and [11,12]).
        """
        return self.start_time < other.end_time and other.start_time < self.end_time


@dataclass
class User:
    """Represents a user in the reservation system."""
    user_id: str
    name: str


@dataclass
class Room:
    """Represents a room in the reservation system."""
    room_id: str
    name: str
    capacity: int


@dataclass
class Reservation:
    """Represents a reservation of a room by a user for a specific time interval."""
    reservation_id: str
    user_id: str
    room_id: str
    time_interval: TimeInterval


class ReservationSystem:
    """Manages users, rooms, and reservations with conflict detection."""
    
    def __init__(self):
        """Initialize the reservation system."""
        self.users: Dict[str, User] = {}
        self.rooms: Dict[str, Room] = {}
        self.reservations: Dict[str, Reservation] = {}
        self.user_reservations: Dict[str, Set[str]] = {}  # user_id -> set of reservation_ids
        self.room_reservations: Dict[str, Set[str]] = {}  # room_id -> set of reservation_ids
    
    def create_user(self, user_id: str, name: str) -> bool:
        """Create a new user with the given ID and name.
        
        Returns:
            bool: True if user was created, False if user already exists
        """
        if user_id in self.users:
            return False
        
        self.users[user_id] = User(user_id=user_id, name=name)
        self.user_reservations[user_id] = set()
        return True
    
    def delete_user(self, user_id: str) -> bool:
        """Delete a user and all their reservations.
        
        Returns:
            bool: True if user was deleted, False if user didn't exist
        """
        if user_id not in self.users:
            return False
        
        # Remove all reservations associated with this user
        for reservation_id in list(self.user_reservations[user_id]):
            self._cancel_reservation(reservation_id)
        
        del self.users[user_id]
        del self.user_reservations[user_id]
        return True
    
    def get_user(self, user_id: str) -> Optional[User]:
        """Get a user by ID.
        
        Returns:
            Optional[User]: The user if found, None otherwise
        """
        return self.users.get(user_id)
    
    def get_all_users(self) -> List[User]:
        """Get all users in the system.
        
        Returns:
            List[User]: List of all users
        """
        return list(self.users.values())
    
    def create_room(self, room_id: str, name: str, capacity: int) -> bool:
        """Create a new room with the given ID, name, and capacity.
        
        Returns:
            bool: True if room was created, False if room already exists
        """
        if room_id in self.rooms:
            return False
        
        self.rooms[room_id] = Room(room_id=room_id, name=name, capacity=capacity)
        self.room_reservations[room_id] = set()
        return True
    
    def delete_room(self, room_id: str) -> bool:
        """Delete a room and all its reservations.
        
        Returns:
            bool: True if room was deleted, False if room didn't exist
        """
        if room_id not in self.rooms:
            return False
        
        # Remove all reservations associated with this room
        for reservation_id in list(self.room_reservations[room_id]):
            self._cancel_reservation(reservation_id)
        
        del self.rooms[room_id]
        del self.room_reservations[room_id]
        return True
    
    def get_room(self, room_id: str) -> Optional[Room]:
        """Get a room by ID.
        
        Returns:
            Optional[Room]: The room if found, None otherwise
        """
        return self.rooms.get(room_id)
    
    def get_all_rooms(self) -> List[Room]:
        """Get all rooms in the system.
        
        Returns:
            List[Room]: List of all rooms
        """
        return list(self.rooms.values())
    
    def create_reservation(
        self, 
        reservation_id: str, 
        user_id: str, 
        room_id: str, 
        start_time: int, 
        end_time: int
    ) -> bool:
        """Create a new reservation if no conflicts exist.
        
        Returns:
            bool: True if reservation was created, False if conflict or invalid entities
        """
        # Check if user and room exist
        if user_id not in self.users or room_id not in self.rooms:
            return False
            
        # Check if reservation already exists
        if reservation_id in self.reservations:
            return False
            
        # Create time interval
        try:
            time_interval = TimeInterval(start_time=start_time, end_time=end_time)
        except ValueError:
            return False
        
        # Check for conflicts with existing reservations for this room
        if self._has_conflict(room_id, time_interval):
            return False
        
        # Create the reservation
        reservation = Reservation(
            reservation_id=reservation_id, 
            user_id=user_id, 
            room_id=room_id, 
            time_interval=time_interval
        )
        
        self.reservations[reservation_id] = reservation
        self.user_reservations[user_id].add(reservation_id)
        self.room_reservations[room_id].add(reservation_id)
        
        return True
    
    def cancel_reservation(self, reservation_id: str) -> bool:
        """Cancel an existing reservation.
        
        Returns:
            bool: True if reservation was cancelled, False if it didn't exist
        """
        return self._cancel_reservation(reservation_id)
    
    def _cancel_reservation(self, reservation_id: str) -> bool:
        """Internal method to cancel a reservation.
        
        Returns:
            bool: True if reservation was cancelled, False if it didn't exist
        """
        if reservation_id not in self.reservations:
            return False
        
        reservation = self.reservations[reservation_id]
        
        # Remove from all tracking structures
        del self.reservations[reservation_id]
        self.user_reservations[reservation.user_id].remove(reservation_id)
        self.room_reservations[reservation.room_id].remove(reservation_id)
        
        return True
    
    def _has_conflict(self, room_id: str, time_interval: TimeInterval) -> bool:
        """Check if a time interval conflicts with existing reservations for a room.
        
        Returns:
            bool: True if conflict exists, False otherwise
        """
        for reservation_id in self.room_reservations.get(room_id, set()):
            existing_reservation = self.reservations[reservation_id]
            if existing_reservation.time_interval.overlaps(time_interval):
                return True
        return False
    
    def get_reservation(self, reservation_id: str) -> Optional[Reservation]:
        """Get a reservation by ID.
        
        Returns:
            Optional[Reservation]: The reservation if found, None otherwise
        """
        return self.reservations.get(reservation_id)
    
    def get_all_reservations(self) -> List[Reservation]:
        """Get all reservations in the system.
        
        Returns:
            List[Reservation]: List of all reservations
        """
        return list(self.reservations.values())
    
    def get_reservations_by_user(self, user_id: str) -> List[Reservation]:
        """Get all reservations for a specific user.
        
        Returns:
            List[Reservation]: List of reservations for the user
        """
        if user_id not in self.user_reservations:
            return []
        
        return [self.reservations[rid] for rid in self.user_reservations[user_id] 
                if rid in self.reservations]
    
    def get_reservations_by_room(self, room_id: str) -> List[Reservation]:
        """Get all reservations for a specific room.
        
        Returns:
            List[Reservation]: List of reservations for the room
        """
        if room_id not in self.room_reservations:
            return []
        
        return [self.reservations[rid] for rid in self.room_reservations[room_id] 
                if rid in self.reservations]
    
    def is_room_available(
        self, 
        room_id: str, 
        start_time: int, 
        end_time: int
    ) -> bool:
        """Check if a room is available for a given time interval.
        
        Returns:
            bool: True if room is available, False otherwise
        """
        if room_id not in self.rooms:
            return False
            
        try:
            time_interval = TimeInterval(start_time=start_time, end_time=end_time)
        except ValueError:
            return False
            
        return not self._has_conflict(room_id, time_interval)
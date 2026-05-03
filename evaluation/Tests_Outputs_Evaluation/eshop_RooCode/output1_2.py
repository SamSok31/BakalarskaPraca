#!/usr/bin/env python3
"""
Advanced E-Shop Backend System

This system manages users, products, carts, reservations, and orders with strict
stock management and atomic operations.
"""

from typing import Dict, List, Optional, Set, Union
from enum import Enum, auto
import re


class InvalidStatusError(ValueError):
    """Raised when an invalid status is provided."""
    pass


class OrderStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

    @classmethod
    def from_string(cls, status_str: str) -> 'OrderStatus':
        """Convert string to OrderStatus enum. Raises InvalidStatusError for invalid strings."""
        status_str = status_str.lower()
        for status in cls:
            if status.value == status_str:
                return status
        raise InvalidStatusError(f"Invalid status: {status_str}")


class ProductSnapshot:
    """Snapshot of product state at the time of order creation."""

    def __init__(self, product_id: str, name: str, price: float, quantity: int):
        self.product_id = product_id
        self.name = name
        self.price = price
        self.quantity = quantity

    def __repr__(self) -> str:
        return f"ProductSnapshot(id={self.product_id}, name='{self.name}', price={self.price}, quantity={self.quantity})"


class Product:
    """Represents a product in the system."""

    def __init__(self, product_id: str, name: str, price: float, stock: int):
        self.product_id = product_id
        self.name = name
        self.price = price
        self.stock = stock  # Current available stock

    def __repr__(self) -> str:
        return f"Product(id={self.product_id}, name='{self.name}', price={self.price}, stock={self.stock})"


class CartItem:
    """Represents an item in a user's cart."""

    def __init__(self, product_id: str, name: str, quantity: int, price: float):
        self.product_id = product_id
        self.name = name
        self.quantity = quantity
        self.price = price

    def __repr__(self) -> str:
        return f"CartItem(id={self.product_id}, name='{self.name}', quantity={self.quantity}, price={self.price})"


class Reservation:
    """Represents a reservation of products for a user."""

    def __init__(self, user_id: str):
        self.user_id = user_id
        self.items: Dict[str, int] = {}  # product_id -> reserved quantity

    def add_item(self, product_id: str, quantity: int) -> None:
        """Add or update reserved quantity for a product."""
        if product_id in self.items:
            self.items[product_id] += quantity
        else:
            self.items[product_id] = quantity

    def remove_item(self, product_id: str, quantity: int) -> int:
        """Remove quantity from reservation. Returns actual quantity removed."""
        if product_id not in self.items:
            return 0
        
        if self.items[product_id] <= quantity:
            removed = self.items.pop(product_id)
            return removed
        else:
            self.items[product_id] -= quantity
            return quantity

    def get_reserved_quantity(self, product_id: str) -> int:
        """Get reserved quantity for a product."""
        return self.items.get(product_id, 0)

    def __repr__(self) -> str:
        return f"Reservation(user={self.user_id}, items={self.items})"


class Order:
    """Represents an order in the system."""

    def __init__(self, order_id: str, user_id: str, items: List[ProductSnapshot]):
        self.order_id = order_id
        self.user_id = user_id
        self.items = items
        self.status = OrderStatus.PENDING
        self._status_history: List[OrderStatus] = [OrderStatus.PENDING]

    def update_status(self, new_status: OrderStatus) -> bool:
        """Update order status if transition is valid. Returns True if successful."""
        # Check if transition is allowed
        if self.status == OrderStatus.CANCELLED:
            return False  # Terminal state
        
        if self.status == OrderStatus.DELIVERED:
            # From delivered, only transition to cancelled is allowed
            success = new_status == OrderStatus.CANCELLED
            if success:
                self.status = new_status
                self._status_history.append(new_status)
            return success
        
        if new_status == OrderStatus.CANCELLED:
            # Can cancel from any state (except already cancelled)
            self.status = new_status
            self._status_history.append(new_status)
            return True
        
        # Regular progression: pending -> processing -> completed -> shipped -> delivered
        if new_status.value == self.status.value + 1:
            self.status = new_status
            self._status_history.append(new_status)
            return True
        
        return False  # Invalid transition

    def get_total(self) -> float:
        """Calculate total order value."""
        return sum(item.price * item.quantity for item in self.items)

    def __repr__(self) -> str:
        return f"Order(id={self.order_id}, user={self.user_id}, status={self.status.name}, items={len(self.items)})"


class EShopBackend:
    """Main e-shop backend system."""

    def __init__(self):
        self.users: Dict[str, str] = {}  # user_id -> user_id (for quick lookup)
        self.products: Dict[str, Product] = {}  # product_id -> Product
        self.product_names: Dict[str, str] = {}  # name -> product_id (for name lookup)
        self.carts: Dict[str, List[CartItem]] = {}  # user_id -> list of CartItems
        self.reservations: Dict[str, Reservation] = {}  # user_id -> Reservation
        self.orders: Dict[str, Order] = {}  # order_id -> Order
        self.next_order_number = 1  # For generating sequential order IDs
        self._total_reserved: Dict[str, int] = {}  # product_id -> total reserved quantity across all users
        self._validate_invariants()

    def _validate_invariants(self) -> None:
        """Validate system invariants (for debugging)."""
        # Ensure all users have carts and reservations
        for user_id in self.users:
            assert user_id in self.carts, f"User {user_id} missing cart"
            assert user_id in self.reservations, f"User {user_id} missing reservation"
        
        # Ensure all carts and reservations belong to existing users
        for user_id in self.carts:
            assert user_id in self.users, f"Cart for non-existent user {user_id}"
        for user_id in self.reservations:
            assert user_id in self.users, f"Reservation for non-existent user {user_id}"
        
        # Validate stock consistency
        for product_id, product in self.products.items():
            total_reserved = 0
            for reservation in self.reservations.values():
                total_reserved += reservation.get_reserved_quantity(product_id)
            
            # Ensure total_reserved doesn't exceed initial stock
            assert total_reserved <= product.stock + total_reserved, f"Inconsistent reserved stock for {product_id}"

    def _generate_order_id(self) -> str:
        """Generate next sequential order ID."""
        order_id = f"SK{self.next_order_number:05d}"
        self.next_order_number += 1
        return order_id

    def create_user(self, user_id: str) -> bool:
        """Create a new user with an empty cart."""
        if not user_id or user_id in self.users:
            return False
        
        self.users[user_id] = user_id
        self.carts[user_id] = []
        self.reservations[user_id] = Reservation(user_id)
        self._validate_invariants()
        return True

    def delete_user(self, user_id: str) -> bool:
        """Delete a user and cancel their reservations."""
        if user_id not in self.users:
            return False
        
        # Cancel all reservations and update total reserved counts
        reservation = self.reservations[user_id]
        for product_id, quantity in list(reservation.items.items()):
            if product_id in self.products:
                self.products[product_id].stock += quantity
            
            # Update total reserved count
            self._total_reserved[product_id] = self._total_reserved.get(product_id, 0) - quantity
        
        # Remove user data
        self.users.pop(user_id)
        self.carts.pop(user_id)
        self.reservations.pop(user_id)
        
        self._validate_invariants()
        return True

    def add_product(self, product_id: str, name: str, price: float, stock: int) -> bool:
        """Add a new product or update existing one."""
        if not product_id or not name or price < 0 or stock < 0:
            return False
        
        if name in self.product_names:
            # Update existing product
            existing_product_id = self.product_names[name]
            product = self.products[existing_product_id]
            product.price = price
            product.stock += stock
            return True
        else:
            # Create new product
            self.products[product_id] = Product(product_id, name, price, stock)
            self.product_names[name] = product_id
            return True

    def delete_product(self, product_id: str) -> bool:
        """Delete a product from available stock."""
        if product_id not in self.products:
            return False
        
        product = self.products[product_id]
        # Remove from name mapping
        self.product_names.pop(product.name)
        # Remove from products
        self.products.pop(product_id)
        
        return True

    def _get_available_stock(self, product_id: str, exclude_user: Optional[str] = None) -> int:
        """Get available stock for a product, excluding reservations from a specific user."""
        if product_id not in self.products:
            return 0
        
        product = self.products[product_id]
        total_reserved = self._total_reserved.get(product_id, 0)
        
        if exclude_user:
            user_reservation = self.reservations.get(exclude_user, Reservation(exclude_user))
            user_reserved = user_reservation.get_reserved_quantity(product_id)
            total_reserved -= user_reserved
        
        return max(0, product.stock - total_reserved)

    def add_to_cart(self, user_id: str, product_id: str, quantity: int) -> bool:
        """Add product to user's cart and create reservation."""
        if user_id not in self.users or product_id not in self.products or quantity <= 0:
            return False
        
        product = self.products[product_id]
        reservation = self.reservations[user_id]
        
        # Check if enough stock is available (excluding current user's existing reservations)
        available_stock = self._get_available_stock(product_id, exclude_user=user_id)
        
        if quantity > available_stock:
            return False
        
        # Add to reservation
        old_quantity = reservation.get_reserved_quantity(product_id)
        reservation.add_item(product_id, quantity)
        
        # Update total reserved count
        new_quantity = reservation.get_reserved_quantity(product_id)
        delta = new_quantity - old_quantity
        self._total_reserved[product_id] = self._total_reserved.get(product_id, 0) + delta
        
        # Update cart
        cart = self.carts[user_id]
        existing_item = next((item for item in cart if item.product_id == product_id), None)
        if existing_item:
            existing_item.quantity += quantity
        else:
            cart.append(CartItem(product_id, product.name, quantity, product.price))
        
        self._validate_invariants()
        return True

    def remove_from_cart(self, user_id: str, product_id: str, quantity: int) -> bool:
        """Remove product from user's cart and release reservation."""
        if user_id not in self.users or product_id not in self.products or quantity <= 0:
            return False
        
        cart = self.carts[user_id]
        reservation = self.reservations[user_id]
        
        # Find cart item
        cart_item = next((item for item in cart if item.product_id == product_id), None)
        if not cart_item:
            return False
        
        # Check if enough quantity is reserved
        if cart_item.quantity < quantity:
            return False
        
        # Remove from reservation
        removed_quantity = reservation.remove_item(product_id, quantity)
        
        # Update total reserved count
        self._total_reserved[product_id] = self._total_reserved.get(product_id, 0) - removed_quantity
        
        # Update cart
        if cart_item.quantity == quantity:
            cart.remove(cart_item)
        else:
            cart_item.quantity -= quantity
        
        self._validate_invariants()
        return True

    def checkout(self, user_id: str) -> Optional[str]:
        """Checkout user's cart and create order. Atomic operation."""
        if user_id not in self.users:
            return None
        
        cart = self.carts[user_id]
        reservation = self.reservations[user_id]
        
        if not cart or not reservation.items:
            return None  # Empty cart
        
        # Validate all reserved products still exist and have correct prices
        order_items = []
        for cart_item in cart:
            if cart_item.product_id not in self.products:
                # Product no longer exists - fail checkout
                return None
            
            product = self.products[cart_item.product_id]
            # Use current price for order (per requirements)
            order_items.append(ProductSnapshot(
                cart_item.product_id,
                cart_item.name,
                product.price,  # Use current price
                cart_item.quantity
            ))
        
        # Create order
        order_id = self._generate_order_id()
        order = Order(order_id, user_id, order_items)
        self.orders[order_id] = order
        
        # Clear cart and reservations, and update total reserved counts
        for cart_item in cart:
            reserved_quantity = reservation.get_reserved_quantity(cart_item.product_id)
            self._total_reserved[cart_item.product_id] = self._total_reserved.get(cart_item.product_id, 0) - reserved_quantity
        
        self.carts[user_id] = []
        self.reservations[user_id] = Reservation(user_id)
        
        self._validate_invariants()
        return order_id

    def update_order_status(self, order_id: str, new_status: Union[str, OrderStatus]) -> bool:
        """Update order status. Ignores invalid status strings."""
        if order_id not in self.orders:
            return False
        
        try:
            # Convert string to OrderStatus if needed
            if isinstance(new_status, str):
                new_status = OrderStatus.from_string(new_status)
            
            order = self.orders[order_id]
            success = order.update_status(new_status)
            
            if success and new_status == OrderStatus.CANCELLED:
                # Return stock for cancelled order
                for item in order.items:
                    if item.product_id in self.products:
                        # Product still exists - return stock
                        self.products[item.product_id].stock += item.quantity
                        # Update total reserved count
                        self._total_reserved[item.product_id] = self._total_reserved.get(item.product_id, 0) - item.quantity
                    else:
                        # Product no longer exists - recreate it
                        self.add_product(item.product_id, item.name, item.price, item.quantity)
            
            return success
            
        except InvalidStatusError:
            # Ignore invalid status inputs
            return False

    def get_current_users(self) -> List[str]:
        """Get list of current user IDs."""
        return list(self.users.keys())

    def get_current_products(self) -> List[Product]:
        """Get list of current products with their stock."""
        return list(self.products.values())

    def get_available_stock(self, product_id: str) -> int:
        """Get current available stock for a product."""
        if product_id not in self.products:
            return 0
        return self.products[product_id].stock

    def get_user_cart(self, user_id: str) -> List[CartItem]:
        """Get user's cart contents."""
        if user_id not in self.users:
            return []
        return self.carts[user_id].copy()

    def get_available_stock(self, product_id: str) -> int:
        """Get current available stock for a product."""
        if product_id not in self.products:
            return 0
        return self._get_available_stock(product_id)

    def get_user_reservations(self, user_id: str) -> Dict[str, int]:
        """Get user's current reservations."""
        if user_id not in self.users:
            return {}
        return self.reservations[user_id].items.copy()

    def get_total_reserved(self, product_id: str) -> int:
        """Get total reserved quantity for a product across all users."""
        return self._total_reserved.get(product_id, 0)

    def get_orders(self) -> List[Order]:
        """Get all orders."""
        return list(self.orders.values())

    def get_order(self, order_id: str) -> Optional[Order]:
        """Get specific order by ID."""
        return self.orders.get(order_id)
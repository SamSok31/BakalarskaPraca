#!/usr/bin/env python3
"""
Advanced E-Shop Backend System

This module implements a comprehensive e-shop backend with user management,
product inventory, cart/reservation system, and order processing.
"""

from typing import Dict, List, Optional, Set
from enum import Enum
import threading


class OrderStatus(Enum):
    """Enum representing possible order statuses and their valid transitions."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

    def valid_transitions(self) -> Set['OrderStatus']:
        """Return the set of valid status transitions from the current status."""
        transitions = {
            OrderStatus.PENDING: {OrderStatus.PROCESSING, OrderStatus.CANCELLED},
            OrderStatus.PROCESSING: {OrderStatus.COMPLETED, OrderStatus.CANCELLED},
            OrderStatus.COMPLETED: {OrderStatus.SHIPPED, OrderStatus.CANCELLED},
            OrderStatus.SHIPPED: {OrderStatus.DELIVERED, OrderStatus.CANCELLED},
            OrderStatus.DELIVERED: {OrderStatus.CANCELLED},
            OrderStatus.CANCELLED: set()  # Terminal state
        }
        return transitions[self]


class User:
    """Class representing a user in the e-shop system."""

    def __init__(self, user_id: str):
        """Initialize a new user with the given ID."""
        self.user_id = user_id
        self.cart = Cart(user_id)


class Product:
    """Class representing a product in the e-shop system."""

    def __init__(self, name: str, price: float, stock: int):
        """Initialize a new product with name, price, and stock quantity."""
        self.name = name
        self.price = price
        self.stock = stock


class CartItem:
    """Class representing an item in a user's cart."""

    def __init__(self, product_name: str, quantity: int, price_at_reservation: float):
        """Initialize a cart item with product name, quantity, and price."""
        self.product_name = product_name
        self.quantity = quantity
        self.price_at_reservation = price_at_reservation


class Cart:
    """Class representing a user's shopping cart."""

    def __init__(self, user_id: str):
        """Initialize an empty cart for the given user."""
        self.user_id = user_id
        self.items: Dict[str, CartItem] = {}  # product_name -> CartItem


class Reservation:
    """Class representing a product reservation in the system."""

    def __init__(self, product_name: str, user_id: str, quantity: int):
        """Initialize a reservation with product name, user ID, and quantity."""
        self.product_name = product_name
        self.user_id = user_id
        self.quantity = quantity


class Order:
    """Class representing an order in the e-shop system."""

    def __init__(self, order_id: str, user_id: str, items: List[CartItem], total_price: float):
        """Initialize an order with ID, user ID, items, and total price."""
        self.order_id = order_id
        self.user_id = user_id
        self.items = items  # Snapshot of items at checkout time
        self.total_price = total_price
        self.status = OrderStatus.PENDING
        self._status_history: List[OrderStatus] = [OrderStatus.PENDING]

    def update_status(self, new_status: OrderStatus) -> bool:
        """Update the order status if the transition is valid. Return success status."""
        if new_status in self.status.valid_transitions():
            self.status = new_status
            self._status_history.append(new_status)
            return True
        return False

    def is_cancelled(self) -> bool:
        """Check if the order is in cancelled state."""
        return self.status == OrderStatus.CANCELLED


class EShopSystem:
    """Main class implementing the e-shop backend system."""

    def __init__(self):
        """Initialize the e-shop system with empty state."""
        self.users: Dict[str, User] = {}  # user_id -> User
        self.products: Dict[str, Product] = {}  # product_name -> Product
        self.reservations: Dict[str, Dict[str, Reservation]] = {}  # user_id -> (product_name -> Reservation)
        self.orders: Dict[str, Order] = {}  # order_id -> Order
        self._next_order_number = 1  # For generating sequential order IDs
        self._lock = threading.Lock()  # For thread safety

    # User management methods

    def create_user(self, user_id: str) -> bool:
        """Create a new user with the given ID. Return True if successful."""
        with self._lock:
            if user_id in self.users or not user_id:
                return False
            self.users[user_id] = User(user_id)
            self.reservations[user_id] = {}  # Initialize empty reservation dict
            return True

    def delete_user(self, user_id: str) -> bool:
        """Delete a user and their cart/reservations. Return True if successful."""
        with self._lock:
            if user_id not in self.users:
                return False

            # Cancel all reservations for this user
            if user_id in self.reservations:
                for product_name, reservation in list(self.reservations[user_id].items()):
                    self._cancel_reservation(user_id, product_name, reservation.quantity)
                del self.reservations[user_id]

            # Remove user
            del self.users[user_id]
            return True

    # Product management methods

    def add_product(self, name: str, price: float, stock: int) -> bool:
        """Add a product or update existing one. Return True if successful."""
        with self._lock:
            if not name or price < 0 or stock < 0:
                return False

            if name in self.products:
                # Update existing product
                product = self.products[name]
                product.price = price
                product.stock += stock
            else:
                # Create new product
                self.products[name] = Product(name, price, stock)
            return True

    def delete_product(self, name: str) -> bool:
        """Delete a product from the system. Return True if successful."""
        with self._lock:
            if name not in self.products:
                return False
            del self.products[name]
            return True

    # Cart management methods

    def add_to_cart(self, user_id: str, product_name: str, quantity: int) -> bool:
        """Add product to user's cart. Return True if successful."""
        with self._lock:
            if (user_id not in self.users or product_name not in self.products or 
                quantity <= 0 or quantity > self.products[product_name].stock):
                return False

            product = self.products[product_name]
            user = self.users[user_id]

            # Check if product is already in cart
            if product_name in user.cart.items:
                # Update existing cart item
                cart_item = user.cart.items[product_name]
                total_requested = cart_item.quantity + quantity
                
                if total_requested > product.stock:
                    return False  # Not enough stock
                
                # Update reservation
                if user_id in self.reservations and product_name in self.reservations[user_id]:
                    self.reservations[user_id][product_name].quantity = total_requested
                
                # Update cart
                cart_item.quantity = total_requested
                cart_item.price_at_reservation = product.price
            else:
                # Create new cart item and reservation
                if user_id not in self.reservations:
                    self.reservations[user_id] = {}
                
                self.reservations[user_id][product_name] = Reservation(product_name, user_id, quantity)
                user.cart.items[product_name] = CartItem(product_name, quantity, product.price)
            
            # Deduct from available stock
            product.stock -= quantity
            return True

    def remove_from_cart(self, user_id: str, product_name: str, quantity: int) -> bool:
        """Remove product from user's cart. Return True if successful."""
        with self._lock:
            if user_id not in self.users or product_name not in self.users[user_id].cart.items:
                return False

            cart_item = self.users[user_id].cart.items[product_name]
            if quantity <= 0 or quantity > cart_item.quantity:
                return False

            # Update or remove reservation
            if quantity == cart_item.quantity:
                # Remove entire reservation
                del self.reservations[user_id][product_name]
                del self.users[user_id].cart.items[product_name]
            else:
                # Reduce reservation
                self.reservations[user_id][product_name].quantity -= quantity
                cart_item.quantity -= quantity
            
            # Return stock if product still exists
            if product_name in self.products:
                self.products[product_name].stock += quantity
            
            return True

    # Checkout methods

    def checkout(self, user_id: str) -> Optional[str]:
        """Checkout user's cart and create an order. Return order ID if successful."""
        with self._lock:
            if user_id not in self.users or not self.users[user_id].cart.items:
                return None

            user = self.users[user_id]
            cart = user.cart
            order_items = []
            total_price = 0.0
            
            # Validate all reserved products still exist and calculate total
            for product_name, cart_item in cart.items.items():
                if product_name not in self.products:
                    # Product no longer exists - checkout fails
                    return None
                
                # Verify price hasn't changed (shouldn't happen due to locking, but double-check)
                if self.products[product_name].price != cart_item.price_at_reservation:
                    return None
                
                order_items.append(CartItem(product_name, cart_item.quantity, cart_item.price_at_reservation))
                total_price += cart_item.quantity * cart_item.price_at_reservation
            
            # Generate order ID
            order_id = f"SK{self._next_order_number:05d}"
            self._next_order_number += 1
            
            # Create order
            order = Order(order_id, user_id, order_items, total_price)
            self.orders[order_id] = order
            
            # Clear cart and reservations
            cart.items.clear()
            if user_id in self.reservations:
                self.reservations[user_id].clear()
            
            return order_id

    # Order management methods

    def update_order_status(self, order_id: str, new_status: OrderStatus) -> bool:
        """Update order status. Return True if successful."""
        with self._lock:
            if order_id not in self.orders:
                return False
            
            order = self.orders[order_id]
            if not order.update_status(new_status):
                return False
            
            # Handle cancellation
            if new_status == OrderStatus.CANCELLED:
                self._handle_order_cancellation(order)
            
            return True

    def _handle_order_cancellation(self, order: Order) -> None:
        """Handle order cancellation by returning stock."""
        for item in order.items:
            if item.product_name in self.products:
                # Product still exists - return stock
                self.products[item.product_name].stock += item.quantity
            else:
                # Product no longer exists - recreate it with original price
                self.products[item.product_name] = Product(item.product_name, item.price_at_reservation, item.quantity)

    def _cancel_reservation(self, user_id: str, product_name: str, quantity: int) -> None:
        """Cancel a reservation and return stock if product exists."""
        if product_name in self.products:
            self.products[product_name].stock += quantity
        
        # Remove reservation if it exists
        if user_id in self.reservations and product_name in self.reservations[user_id]:
            del self.reservations[user_id][product_name]

    # State access methods

    def get_users(self) -> List[str]:
        """Return list of current user IDs."""
        with self._lock:
            return list(self.users.keys())

    def get_products(self) -> Dict[str, Dict[str, float | int]]:
        """Return dictionary of current products with their price and stock."""
        with self._lock:
            return {
                name: {"price": product.price, "stock": product.stock}
                for name, product in self.products.items()
            }

    def get_available_stock(self) -> Dict[str, int]:
        """Return dictionary of current available stock."""
        with self._lock:
            return {name: product.stock for name, product in self.products.items()}

    def get_user_cart(self, user_id: str) -> Dict[str, Dict[str, float | int]]:
        """Return dictionary of items in user's cart."""
        with self._lock:
            if user_id not in self.users:
                return {}
            return {
                product_name: {
                    "quantity": item.quantity,
                    "price": item.price_at_reservation
                }
                for product_name, item in self.users[user_id].cart.items.items()
            }

    def get_user_reservations(self, user_id: str) -> Dict[str, int]:
        """Return dictionary of user's current reservations."""
        with self._lock:
            if user_id not in self.reservations:
                return {}
            return {
                product_name: reservation.quantity
                for product_name, reservation in self.reservations[user_id].items()
            }

    def get_orders(self) -> Dict[str, Dict]:
        """Return dictionary of all orders with their details."""
        with self._lock:
            orders_dict = {}
            for order_id, order in self.orders.items():
                orders_dict[order_id] = {
                    "user_id": order.user_id,
                    "items": [
                        {
                            "product_name": item.product_name,
                            "quantity": item.quantity,
                            "price": item.price_at_reservation
                        }
                        for item in order.items
                    ],
                    "total_price": order.total_price,
                    "status": order.status.value
                }
            return orders_dict

    def get_order_status(self, order_id: str) -> Optional[str]:
        """Return the status of an order, or None if order doesn't exist."""
        with self._lock:
            if order_id not in self.orders:
                return None
            return self.orders[order_id].status.value
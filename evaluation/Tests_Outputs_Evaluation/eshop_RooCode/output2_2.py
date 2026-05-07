"""
Advanced E-Shop Backend System

This module implements a comprehensive e-shop backend with user management,
product inventory, shopping carts, reservations, and order processing.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Set
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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
        return transitions.get(self, set())


@dataclass
class ProductSnapshot:
    """Snapshot of product information at the time of order creation."""
    product_id: str
    name: str
    price: float
    quantity: int


@dataclass
class Order:
    """Represents an order in the system."""
    order_id: str
    user_id: str
    items: List[ProductSnapshot] = field(default_factory=list)
    status: OrderStatus = OrderStatus.PENDING
    total_amount: float = 0.0

    def calculate_total(self) -> float:
        """Calculate the total amount of the order."""
        return sum(item.price * item.quantity for item in self.items)

    def update_status(self, new_status: OrderStatus) -> bool:
        """
        Update the order status if the transition is valid.
        Returns True if the status was updated, False otherwise.
        """
        if new_status in self.status.valid_transitions():
            self.status = new_status
            logger.info(f"Order {self.order_id} status updated to {new_status.value}")
            return True
        logger.warning(f"Invalid status transition for order {self.order_id}: {self.status.value} -> {new_status.value}")
        return False


@dataclass
class Reservation:
    """Represents a reservation of products in a user's cart."""
    product_id: str
    quantity: int


@dataclass
class Cart:
    """Represents a user's shopping cart."""
    user_id: str
    reservations: Dict[str, Reservation] = field(default_factory=dict)  # product_id -> Reservation

    def is_empty(self) -> bool:
        """Check if the cart is empty."""
        return len(self.reservations) == 0

    def get_reserved_quantity(self, product_id: str) -> int:
        """Get the reserved quantity for a specific product."""
        return self.reservations.get(product_id, Reservation(product_id, 0)).quantity

    def clear(self) -> None:
        """Clear all reservations in the cart."""
        self.reservations.clear()


@dataclass
class Product:
    """Represents a product in the inventory."""
    product_id: str
    name: str
    price: float
    stock: int  # Current available stock (excluding reservations)

    def update_stock(self, quantity: int) -> bool:
        """
        Update the product's available stock by adding the specified quantity.
        Returns True if the update was successful, False otherwise.
        """
        if self.stock + quantity < 0:
            logger.warning(f"Cannot update stock for product {self.product_id}: insufficient available stock. Current: {self.stock}, Attempted: {quantity}")
            return False
        self.stock += quantity
        logger.debug(f"Product {self.product_id} available stock updated: {self.stock - quantity} -> {self.stock}")
        return True


@dataclass
class User:
    """Represents a user in the system."""
    user_id: str


class EShop:
    """Main e-shop backend system."""

    def __init__(self):
        self.users: Dict[str, User] = {}  # user_id -> User
        self.products: Dict[str, Product] = {}  # product_id -> Product
        self.carts: Dict[str, Cart] = {}  # user_id -> Cart
        self.orders: Dict[str, Order] = {}  # order_id -> Order
        self.next_order_number: int = 1  # For generating sequential order IDs
        logger.info("EShop backend system initialized")

    def create_user(self, user_id: str) -> bool:
        """
        Create a new user with the given ID.
        Returns True if the user was created, False if the user already exists.
        """
        if not user_id or user_id in self.users:
            logger.warning(f"User creation failed: invalid ID or user {user_id} already exists")
            return False

        self.users[user_id] = User(user_id)
        self.carts[user_id] = Cart(user_id)
        logger.info(f"User {user_id} created with empty cart")
        return True

    def delete_user(self, user_id: str) -> bool:
        """
        Delete a user and clean up their resources.
        Returns True if the user was deleted, False if the user didn't exist.
        """
        if user_id not in self.users:
            logger.warning(f"User deletion failed: user {user_id} does not exist")
            return False

        # Cancel all reservations and return stock to available stock
        cart = self.carts[user_id]
        for reservation in cart.reservations.values():
            product_id = reservation.product_id
            if product_id in self.products:
                # Return reserved quantity to available stock
                self.products[product_id].update_stock(reservation.quantity)
            # If product no longer exists, just remove the reservation (no stock to return)

        # Remove user and cart
        del self.users[user_id]
        del self.carts[user_id]
        logger.info(f"User {user_id} deleted and their reservations cancelled")
        return True

    def add_product(self, product_id: str, name: str, price: float, stock: int) -> bool:
        """
        Add a new product or update an existing one.
        Returns True if the product was added/updated, False if the operation failed.
        """
        if not product_id or not name or price < 0 or stock < 0:
            logger.warning(f"Product addition failed: invalid parameters for product {product_id}")
            return False

        if product_id in self.products:
            # Update existing product - INCREASE current available stock, don't overwrite
            product = self.products[product_id]
            product.price = price  # Update price
            product.update_stock(stock)  # INCREASE current available stock
            logger.info(f"Product {product_id} updated: price={price}, stock increased by {stock}. New available stock: {product.stock}")
        else:
            # Add new product
            self.products[product_id] = Product(product_id, name, price, stock)
            logger.info(f"Product {product_id} added: name={name}, price={price}, available stock={stock}")
        return True

    def delete_product(self, product_id: str) -> bool:
        """
        Delete a product from the current available stock system.
        Returns True if the product was deleted, False if it didn't exist.
        """
        if product_id not in self.products:
            logger.warning(f"Product deletion failed: product {product_id} does not exist")
            return False

        del self.products[product_id]
        logger.info(f"Product {product_id} deleted from available stock")
        return True

    def modify_cart(self, user_id: str, product_id: str, quantity: int) -> bool:
        """
        Modify a user's cart by adding or removing products.
        Positive quantity adds to cart, negative quantity removes from cart.
        Returns True if the cart was modified, False otherwise.
        """
        if user_id not in self.users or product_id not in self.products:
            logger.warning(f"Cart modification failed: user {user_id} or product {product_id} does not exist")
            return False

        if quantity == 0:
            logger.info(f"Cart modification ignored: zero quantity for product {product_id}")
            return False

        product = self.products[product_id]
        cart = self.carts[user_id]
        current_reserved = cart.get_reserved_quantity(product_id)
        new_quantity = current_reserved + quantity

        if quantity > 0:  # Adding to cart
            if quantity < 0:
                logger.warning(f"Cart modification failed: negative quantity {quantity} for adding to cart")
                return False
            if new_quantity <= 0:
                logger.warning(f"Cart modification failed: invalid quantity {quantity} for product {product_id}")
                return False

            available_stock = product.stock
            if new_quantity > available_stock:
                logger.warning(f"Cart modification failed: insufficient stock for product {product_id}. Requested: {new_quantity}, Available: {available_stock}")
                return False

            # Update reservation and stock
            if product_id in cart.reservations:
                cart.reservations[product_id].quantity = new_quantity
            else:
                cart.reservations[product_id] = Reservation(product_id, new_quantity)
            product.update_stock(-quantity)
            logger.info(f"Added {quantity} of product {product_id} to user {user_id}'s cart")
            return True

        else:  # Removing from cart (quantity is negative)
            if quantity > 0:
                logger.warning(f"Cart modification failed: positive quantity {quantity} for removing from cart")
                return False
            if current_reserved < -quantity:
                logger.warning(f"Cart modification failed: cannot remove {-quantity} of product {product_id}, only {current_reserved} reserved")
                return False

            # Update reservation and stock
            if new_quantity > 0:
                cart.reservations[product_id].quantity = new_quantity
            else:
                del cart.reservations[product_id]
            product.update_stock(-quantity)  # quantity is negative, so this adds to stock
            logger.info(f"Removed {-quantity} of product {product_id} from user {user_id}'s cart")
            return True

    def checkout(self, user_id: str) -> Optional[str]:
        """
        Perform checkout for a user's cart.
        Returns the order ID if checkout was successful, None otherwise.
        """
        if user_id not in self.users:
            logger.warning(f"Checkout failed: user {user_id} does not exist")
            return None

        cart = self.carts[user_id]
        if cart.is_empty():
            logger.warning(f"Checkout failed: user {user_id} has an empty cart")
            return None

        # Check if all reserved products still exist in stock and validate consistency
        for reservation in cart.reservations.values():
            if reservation.product_id not in self.products:
                logger.warning(f"Checkout failed: product {reservation.product_id} no longer exists in stock")
                return None
            # Verify that the reserved quantity is consistent with available stock
            # This should always be true if the system is consistent
            product = self.products[reservation.product_id]
            if product.stock < 0:
                logger.warning(f"Checkout failed: inconsistent stock for product {reservation.product_id}")
                return None

        # Create order items from reservations
        order_items = []
        for reservation in cart.reservations.values():
            product = self.products[reservation.product_id]
            order_items.append(ProductSnapshot(
                product_id=product.product_id,
                name=product.name,
                price=product.price,
                quantity=reservation.quantity
            ))

        # Generate order ID
        order_id = f"SK{self.next_order_number:05d}"
        self.next_order_number += 1

        # Create and store the order
        order = Order(
            order_id=order_id,
            user_id=user_id,
            items=order_items,
            total_amount=sum(item.price * item.quantity for item in order_items)
        )
        self.orders[order_id] = order

        # Clear the cart (reservations are already deducted from stock)
        cart.clear()
        logger.info(f"Checkout successful for user {user_id}. Order ID: {order_id}")
        return order_id

    def update_order_status(self, order_id: str, new_status: OrderStatus) -> bool:
        """
        Update the status of an order.
        Returns True if the status was updated, False otherwise.
        """
        if order_id not in self.orders:
            logger.warning(f"Order status update failed: order {order_id} does not exist")
            return False

        order = self.orders[order_id]
        if order.update_status(new_status):
            # Handle cancellation logic
            if new_status == OrderStatus.CANCELLED:
                self._handle_order_cancellation(order)
            return True
        return False

    def _handle_order_cancellation(self, order: Order) -> None:
        """Handle the logic when an order is cancelled."""
        for item in order.items:
            if item.product_id in self.products:
                # Product exists, return stock to available stock
                self.products[item.product_id].update_stock(item.quantity)
                logger.debug(f"Returned {item.quantity} of product {item.product_id} to available stock")
            else:
                # Product doesn't exist, recreate it with the price stored in the order
                self.products[item.product_id] = Product(
                    product_id=item.product_id,
                    name=item.name,
                    price=item.price,
                    stock=item.quantity  # Return the stock that was reserved in the order
                )
                logger.debug(f"Recreated product {item.product_id} with stock {item.quantity} from cancelled order")
        logger.info(f"Order {order.order_id} cancelled and stock returned/recreated")

    # State access methods
    def get_users(self) -> List[str]:
        """Get a list of all user IDs."""
        return list(self.users.keys())

    def get_products(self) -> Dict[str, Dict[str, object]]:
        """Get a dictionary of all products with their details."""
        return {
            pid: {
                'name': p.name,
                'price': p.price,
                'stock': p.stock
            }
            for pid, p in self.products.items()
        }

    def get_available_stock(self) -> Dict[str, int]:
        """Get the current available stock for all products."""
        return {pid: p.stock for pid, p in self.products.items()}

    def get_user_cart(self, user_id: str) -> Optional[Dict[str, int]]:
        """Get the contents of a user's cart as a dictionary of product_id -> quantity."""
        if user_id not in self.carts:
            return None
        return {res.product_id: res.quantity for res in self.carts[user_id].reservations.values()}

    def get_user_reservations(self, user_id: str) -> Optional[Dict[str, int]]:
        """Get a user's reservations (same as cart contents)."""
        return self.get_user_cart(user_id)

    def get_orders(self) -> Dict[str, Dict[str, object]]:
        """Get a dictionary of all orders with their details."""
        return {
            oid: {
                'user_id': order.user_id,
                'items': [{
                    'product_id': item.product_id,
                    'name': item.name,
                    'price': item.price,
                    'quantity': item.quantity
                } for item in order.items],
                'status': order.status.value,
                'total_amount': order.total_amount
            }
            for oid, order in self.orders.items()
        }

    def get_order_status(self, order_id: str) -> Optional[str]:
        """Get the status of a specific order."""
        if order_id not in self.orders:
            return None
        return self.orders[order_id].status.value
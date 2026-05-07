# Let's design and implement an advanced e-shop backend system in Python.
# The system will manage users, products, carts, reservations, and orders, ensuring correct handling of stock.

from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum, auto


class OrderStatus(Enum):
    PENDING = auto()
    PROCESSING = auto()
    COMPLETED = auto()
    SHIPPED = auto()
    DELIVERED = auto()
    CANCELLED = auto()


@dataclass
class Product:
    name: str
    price: float
    stock: int


@dataclass
class User:
    user_id: str
    cart: Dict[str, int] = field(default_factory=dict)
    reservations: Dict[str, int] = field(default_factory=dict)


@dataclass
class Order:
    order_id: str
    user_id: str
    products: Dict[str, Tuple[int, float]]  # {product_name: (quantity, price)}
    status: OrderStatus


class EShopBackend:
    def __init__(self):
        self.users: Dict[str, User] = {}
        self.products: Dict[str, Product] = {}
        self.orders: List[Order] = []
        self.next_order_id = 1

    def create_user(self, user_id: str) -> None:
        if user_id not in self.users:
            self.users[user_id] = User(user_id=user_id)

    def delete_user(self, user_id: str) -> None:
        if user_id in self.users:
            user = self.users[user_id]
            # Return reserved quantities to stock
            for product_name, quantity in user.reservations.items():
                if product_name in self.products:
                    self.products[product_name].stock += quantity
            del self.users[user_id]

    def add_product(self, name: str, price: float, stock: int) -> None:
        if name in self.products:
            self.products[name].stock += stock
            self.products[name].price = price
        else:
            self.products[name] = Product(name=name, price=price, stock=stock)

    def delete_product(self, name: str) -> None:
        if name in self.products:
            del self.products[name]

    def add_to_cart(self, user_id: str, product_name: str, quantity: int) -> None:
        if user_id not in self.users or product_name not in self.products or quantity <= 0:
            return

        user = self.users[user_id]
        product = self.products[product_name]

        if product.stock >= quantity:
            user.cart[product_name] = user.cart.get(product_name, 0) + quantity
            user.reservations[product_name] = user.reservations.get(product_name, 0) + quantity
            product.stock -= quantity

    def remove_from_cart(self, user_id: str, product_name: str, quantity: int) -> None:
        if user_id not in self.users or product_name not in self.users[user_id].cart or quantity <= 0:
            return

        user = self.users[user_id]
        if user.cart[product_name] < quantity:
            return

        user.cart[product_name] -= quantity
        user.reservations[product_name] -= quantity

        if user.reservations[product_name] == 0:
            del user.reservations[product_name]
            if user.cart[product_name] == 0:
                del user.cart[product_name]

        if product_name in self.products:
            self.products[product_name].stock += quantity

    def checkout(self, user_id: str) -> Optional[str]:
        if user_id not in self.users:
            return None

        user = self.users[user_id]
        if not user.cart:
            return None

        # Check if all reserved products still exist
        for product_name in user.reservations:
            if product_name not in self.products:
                return None

        # Create order
        order_id = f"SK{self.next_order_id:05d}"
        self.next_order_id += 1

        order_products = {}
        for product_name, quantity in user.cart.items():
            order_products[product_name] = (quantity, self.products[product_name].price)

        order = Order(
            order_id=order_id,
            user_id=user_id,
            products=order_products,
            status=OrderStatus.PENDING
        )

        self.orders.append(order)

        # Clear cart and reservations
        user.cart.clear()
        user.reservations.clear()

        return order_id

    def update_order_status(self, order_id: str, new_status: OrderStatus) -> None:
        for order in self.orders:
            if order.order_id == order_id:
                # Check if the transition is valid
                if new_status == OrderStatus.CANCELLED:
                    # Handle cancellation
                    for product_name, (quantity, price) in order.products.items():
                        if product_name in self.products:
                            self.products[product_name].stock += quantity
                        else:
                            self.products[product_name] = Product(name=product_name, price=price, stock=quantity)
                    order.status = new_status
                else:
                    # Check if the transition is allowed
                    if (
                        (order.status == OrderStatus.PENDING and new_status == OrderStatus.PROCESSING) or
                        (order.status == OrderStatus.PROCESSING and new_status == OrderStatus.COMPLETED) or
                        (order.status == OrderStatus.COMPLETED and new_status == OrderStatus.SHIPPED) or
                        (order.status == OrderStatus.SHIPPED and new_status == OrderStatus.DELIVERED)
                    ):
                        order.status = new_status
                break

    def get_current_state(self) -> Dict:
        return {
            "users": list(self.users.keys()),
            "products": {name: {"price": p.price, "stock": p.stock} for name, p in self.products.items()},
            "available_stock": {name: p.stock for name, p in self.products.items()},
            "carts": {uid: list(u.cart.items()) for uid, u in self.users.items()},
            "reservations": {uid: list(u.reservations.items()) for uid, u in self.users.items()},
            "orders": [
                {
                    "order_id": o.order_id,
                    "user_id": o.user_id,
                    "products": list(o.products.items()),
                    "status": o.status.name
                }
                for o in self.orders
            ]
        }
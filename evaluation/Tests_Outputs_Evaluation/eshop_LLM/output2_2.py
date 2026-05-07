from typing import Dict, List, Optional, Set, Tuple

class Product:
    def __init__(self, name: str, price: float, stock: int):
        self.name = name
        self.price = price
        self.stock = stock

class User:
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.cart: Dict[str, int] = {}  # {product_name: quantity}
        self.reservations: Dict[str, int] = {}  # {product_name: quantity}

class Order:
    def __init__(self, order_id: str, user_id: str, products: Dict[str, Tuple[int, float]], status: str):
        self.order_id = order_id
        self.user_id = user_id
        self.products = products  # {product_name: (quantity, price)}
        self.status = status

class EShopBackend:
    def __init__(self):
        self.users: Dict[str, User] = {}
        self.products: Dict[str, Product] = {}
        self.orders: Dict[str, Order] = {}
        self.next_order_id = 1

    def create_user(self, user_id: str) -> None:
        if user_id not in self.users:
            self.users[user_id] = User(user_id)

    def delete_user(self, user_id: str) -> None:
        if user_id in self.users:
            user = self.users[user_id]
            # Return reserved products to stock
            for product_name, quantity in user.reservations.items():
                if product_name in self.products:
                    self.products[product_name].stock += quantity
            del self.users[user_id]

    def add_product(self, name: str, price: float, stock: int) -> None:
        if stock < 0:
            return  # Ignore negative stock
        if name in self.products:
            self.products[name].stock += stock
            self.products[name].price = price
        else:
            self.products[name] = Product(name, price, stock)

    def delete_product(self, name: str) -> None:
        if name in self.products:
            del self.products[name]

    def add_to_cart(self, user_id: str, product_name: str, quantity: int) -> None:
        if (user_id not in self.users or
            product_name not in self.products or
            quantity <= 0 or
            self.products[product_name].stock < quantity):
            return
        user = self.users[user_id]
        product = self.products[product_name]
        if product_name in user.cart:
            user.cart[product_name] += quantity
        else:
            user.cart[product_name] = quantity
        if product_name in user.reservations:
            user.reservations[product_name] += quantity
        else:
            user.reservations[product_name] = quantity
        product.stock -= quantity

    def remove_from_cart(self, user_id: str, product_name: str, quantity: int) -> None:
        if (user_id not in self.users or
            product_name not in self.users[user_id].cart or
            quantity <= 0):
            return
        user = self.users[user_id]
        if user.cart[product_name] < quantity:
            return
        user.cart[product_name] -= quantity
        if user.cart[product_name] == 0:
            del user.cart[product_name]
        if product_name in user.reservations:
            user.reservations[product_name] -= quantity
            if user.reservations[product_name] == 0:
                del user.reservations[product_name]
            if product_name in self.products:
                self.products[product_name].stock += quantity

    def checkout(self, user_id: str) -> Optional[str]:
        if user_id not in self.users or not self.users[user_id].cart:
            return None
        user = self.users[user_id]
        # Check if all reserved products still exist
        for product_name in user.reservations:
            if product_name not in self.products:
                return None
        # Create order
        order_products = {}
        for product_name, quantity in user.cart.items():
            order_products[product_name] = (quantity, self.products[product_name].price)
        order_id = f"SK{self.next_order_id:05d}"
        self.orders[order_id] = Order(order_id, user_id, order_products, "pending")
        self.next_order_id += 1
        # Clear cart and reservations
        user.cart.clear()
        user.reservations.clear()
        return order_id

    def update_order_status(self, order_id: str, new_status: str) -> None:
        if order_id not in self.orders:
            return
        order = self.orders[order_id]
        if order.status == "cancelled":
            return  # Terminal state
        if new_status == "cancelled":
            order.status = "cancelled"
            for product_name, (quantity, price) in order.products.items():
                if product_name in self.products:
                    self.products[product_name].stock += quantity
                else:
                    self.products[product_name] = Product(product_name, price, quantity)
        else:
            valid_transitions = {
                "pending": ["processing"],
                "processing": ["completed"],
                "completed": ["shipped"],
                "shipped": ["delivered"],
                "delivered": [],
                "cancelled": []
            }
            if new_status in valid_transitions[order.status]:
                order.status = new_status

    def get_available_stock(self) -> Dict[str, int]:
        stock = {}
        for product_name, product in self.products.items():
            stock[product_name] = product.stock
        return stock

    def get_user_cart(self, user_id: str) -> Dict[str, int]:
        if user_id in self.users:
            return self.users[user_id].cart.copy()
        return {}

    def get_user_reservations(self, user_id: str) -> Dict[str, int]:
        if user_id in self.users:
            return self.users[user_id].reservations.copy()
        return {}

    def get_orders(self) -> Dict[str, Dict]:
        return {
            order_id: {
                "user_id": order.user_id,
                "products": order.products,
                "status": order.status
            }
            for order_id, order in self.orders.items()
        }
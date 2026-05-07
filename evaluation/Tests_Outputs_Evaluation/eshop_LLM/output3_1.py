from typing import Dict, List, Optional, Set, Tuple

class Product:
    def __init__(self, name: str, price: float, stock: int):
        self.name = name
        self.price = price
        self.stock = stock

    def __repr__(self):
        return f"Product(name={self.name}, price={self.price}, stock={self.stock})"

class User:
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.cart: Dict[str, int] = {}  # {product_name: quantity}
        self.reservations: Dict[str, int] = {}  # {product_name: quantity}

    def __repr__(self):
        return f"User(id={self.user_id}, cart={self.cart}, reservations={self.reservations})"

class Order:
    def __init__(self, order_id: str, user_id: str, products: Dict[str, Tuple[int, float]], status: str = "pending"):
        self.order_id = order_id
        self.user_id = user_id
        self.products = products  # {product_name: (quantity, price)}
        self.status = status

    def __repr__(self):
        return f"Order(id={self.order_id}, user_id={self.user_id}, products={self.products}, status={self.status})"

class EShopBackend:
    def __init__(self):
        self.users: Dict[str, User] = {}
        self.products: Dict[str, Product] = {}
        self.orders: Dict[str, Order] = {}
        self.order_counter = 1

    def create_user(self, user_id: str) -> None:
        if user_id not in self.users:
            self.users[user_id] = User(user_id)

    def delete_user(self, user_id: str) -> None:
        if user_id in self.users:
            user = self.users[user_id]
            for product_name, quantity in user.reservations.items():
                if product_name in self.products:
                    self.products[product_name].stock += quantity
            del self.users[user_id]

    def add_product(self, name: str, price: float, stock: int) -> None:
        if name in self.products:
            self.products[name].stock += stock
            self.products[name].price = price
        else:
            self.products[name] = Product(name, price, stock)

    def delete_product(self, name: str) -> None:
        if name in self.products:
            del self.products[name]

    def add_to_cart(self, user_id: str, product_name: str, quantity: int) -> None:
        if user_id not in self.users or product_name not in self.products or quantity <= 0:
            return
        user = self.users[user_id]
        product = self.products[product_name]
        if product.stock >= quantity:
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
        if user_id not in self.users or product_name not in self.products or quantity <= 0:
            return
        user = self.users[user_id]
        if product_name in user.cart and user.cart[product_name] >= quantity:
            user.cart[product_name] -= quantity
            if user.cart[product_name] == 0:
                del user.cart[product_name]
            if product_name in user.reservations and user.reservations[product_name] >= quantity:
                user.reservations[product_name] -= quantity
                if user.reservations[product_name] == 0:
                    del user.reservations[product_name]
                if product_name in self.products:
                    self.products[product_name].stock += quantity

    def checkout(self, user_id: str) -> Optional[str]:
        if user_id not in self.users or not self.users[user_id].cart:
            return None
        user = self.users[user_id]
        products_to_order = {}
        for product_name, quantity in user.cart.items():
            if product_name not in self.products:
                return None
            products_to_order[product_name] = (quantity, self.products[product_name].price)
        order_id = f"SK{self.order_counter:05d}"
        self.order_counter += 1
        self.orders[order_id] = Order(order_id, user_id, products_to_order)
        user.cart.clear()
        user.reservations.clear()
        return order_id

    def update_order_status(self, order_id: str, new_status: str) -> None:
        if order_id not in self.orders:
            return
        order = self.orders[order_id]
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

    def get_state(self) -> Dict:
        return {
            "users": self.users,
            "products": self.products,
            "orders": self.orders,
            "available_stock": {name: product.stock for name, product in self.products.items()}
        }
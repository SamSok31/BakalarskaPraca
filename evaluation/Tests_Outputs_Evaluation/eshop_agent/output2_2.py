class User:
    def __init__(self, user_id: str) -> None:
        self.user_id = user_id
        self.cart = {}

class Product:
    def __init__(self, name: str, price: float):
        self.name = name
        self.price = price

class Order:
    def __init__(self, order_id: str, status: str, products: dict[str, dict]):
        self.order_id = order_id
        self.status = status
        self.products = products

class EShopBackend:
    def __init__(self):
        self.users = {}
        self.products = {}
        self.orders = {}
        self.next_order_id = 1
        self.stock = {}
        self.reserved_stock = {}

    def create_user(self, user_id: str) -> bool:
        if not user_id or user_id in self.users:
            return False

        new_user = User(user_id)
        self.users[user_id] = new_user
        return True

    def delete_user(self, user_id: str) -> bool:
        if user_id not in self.users:
            return False

        user = self.users[user_id]
        for product_name, quantity in list(user.cart.items()):
            if product_name in self.products and product_name in self.stock:
                self.stock[product_name] += quantity
            if product_name in self.reserved_stock:
                del self.reserved_stock[product_name]
            del user.cart[product_name]

        del self.users[user_id]
        return True

    def add_or_update_product(self, name: str, price: float, stock: int) -> bool:
        if not name.strip() or price < 0 or stock < 0:
            return False

        if name in self.products:
            self.products[name].price = price
            self.stock[name] += stock
        else:
            new_product = Product(name, price)
            self.products[name] = new_product
            self.stock[name] = stock

        return True

    def delete_product(self, name: str) -> bool:
        if name not in self.products:
            return False

        del self.products[name]
        del self.stock[name]
        if name in self.reserved_stock:
            del self.reserved_stock[name]
        return True

    def modify_cart(self, user_id: str, product_name: str, quantity: int) -> bool:
        if user_id not in self.users or product_name not in self.products:
            return False

        if quantity == 0:
            return False

        user = self.users[user_id]
        product = self.products[product_name]

        if quantity > 0:
            if product_name not in self.stock or self.stock[product_name] < quantity:
                return False

            self.stock[product_name] -= quantity
            if product_name in self.reserved_stock:
                self.reserved_stock[product_name] += quantity
            else:
                self.reserved_stock[product_name] = quantity

            if product_name in user.cart:
                user.cart[product_name] += quantity
            else:
                user.cart[product_name] = quantity
        else:
            abs_quantity = abs(quantity)
            if product_name not in user.cart or user.cart[product_name] < abs_quantity:
                return False

            user.cart[product_name] -= abs_quantity
            if user.cart[product_name] == 0:
                del user.cart[product_name]

            if product_name in self.stock:
                self.stock[product_name] += abs_quantity
            if product_name in self.reserved_stock:
                self.reserved_stock[product_name] -= abs_quantity
                if self.reserved_stock[product_name] == 0:
                    del self.reserved_stock[product_name]

        return True

    def checkout(self, user_id: str) -> tuple[bool, str | None]:
        if user_id not in self.users or not self.users[user_id].cart:
            return False, None

        user = self.users[user_id]
        cart = user.cart
        order_items = {}

        for product_name, quantity in cart.items():
            if product_name not in self.products or product_name not in self.stock:
                return False, None

            if self.stock[product_name] < quantity:
                return False, None

            product = self.products[product_name]
            order_items[product_name] = {
                'price': product.price,
                'quantity': quantity
            }

        order_id = f"SK{self.next_order_id:05d}"
        order = Order(
            order_id=order_id,
            products=order_items,
            status='pending'
        )

        try:
            for product_name, quantity in cart.items():
                if product_name in self.reserved_stock:
                    del self.reserved_stock[product_name]

            self.orders[order_id] = order
            self.next_order_id += 1
            user.cart.clear()

            return True, order_id
        except:
            for product_name, quantity in cart.items():
                if product_name in self.stock:
                    self.stock[product_name] += quantity
                if product_name in self.reserved_stock:
                    self.reserved_stock[product_name] += quantity
            return False, None

    def update_order_status(self, order_id: str, target_status: str) -> bool:
        if order_id not in self.orders:
            return False

        order = self.orders[order_id]
        current_status = order.status

        valid_transitions = {
            'pending': ['processing', 'cancelled'],
            'processing': ['completed', 'cancelled'],
            'completed': ['shipped', 'cancelled'],
            'shipped': ['delivered', 'cancelled'],
            'delivered': ['cancelled']
        }

        if target_status not in valid_transitions.get(current_status, []):
            return False

        valid_statuses = ['pending', 'processing', 'completed', 'shipped', 'delivered', 'cancelled']
        if target_status not in valid_statuses:
            return False

        if target_status == 'cancelled':
            for product_name, product_data in order.products.items():
                if product_name in self.products:
                    self.stock[product_name] += product_data['quantity']
                else:
                    self.products[product_name] = Product(name=product_name, price=product_data['price'])
                    self.stock[product_name] = product_data['quantity']

        order.status = target_status
        return True

    def get_system_state(self) -> dict:
        state = {
            'users': {user_id: {'cart': user.cart} for user_id, user in self.users.items()},
            'products': {name: {'price': product.price, 'stock': self.stock[name]}
                        for name, product in self.products.items()},
            'stock': self.stock.copy(),
            'reserved_stock': self.reserved_stock.copy(),
            'orders': {order_id: {'status': order.status}
                      for order_id, order in self.orders.items()}
        }
        return state
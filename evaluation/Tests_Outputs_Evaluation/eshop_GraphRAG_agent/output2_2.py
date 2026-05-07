class EShopSystem:
    def __init__(self):
        self.users = {}
        self.products = {}
        self.orders = {}
        self.next_order_id = 1

    def create_user(self, user_id):
        if user_id not in self.users:
            self.users[user_id] = {'cart': {}}

    def delete_user(self, user_id: str) -> None:
        if user_id not in self.users:
            return

        user_cart = self.users[user_id]['cart'].copy()
        for product_name, quantity in user_cart.items():
            if product_name in self.products:
                self.products[product_name]['stock'] += quantity
            self.users[user_id]['cart'].pop(product_name, None)

        del self.users[user_id]

    def add_or_update_product(self, name, price, stock):
        if not isinstance(name, str) or not name.strip() or price < 0 or stock < 0:
            return

        if name in self.products:
            self.products[name]['price'] = price
            self.products[name]['stock'] += stock
        else:
            self.products[name] = {
                'price': price,
                'stock': stock
            }

    def delete_product(self, name: str) -> None:
        if name in self.products:
            del self.products[name]

    def add_to_cart(self, user_id: str, product_name: str, quantity: int) -> None:
        if user_id not in self.users or product_name not in self.products or quantity <= 0:
            return

        product = self.products[product_name]
        user = self.users[user_id]

        if product['stock'] < quantity:
            return

        if product_name in user['cart']:
            user['cart'][product_name] += quantity
        else:
            user['cart'][product_name] = quantity

        product['stock'] -= quantity

    def remove_from_cart(self, user_id: str, product_name: str, quantity: int) -> None:
        if user_id not in self.users or product_name not in self.users[user_id]['cart'] or quantity <= 0:
            return

        if product_name not in self.products:
            del self.users[user_id]['cart'][product_name]
            return

        reserved_quantity = self.users[user_id]['cart'][product_name]

        if quantity > reserved_quantity:
            return

        if quantity >= reserved_quantity:
            del self.users[user_id]['cart'][product_name]
            self.products[product_name]['stock'] += reserved_quantity
        else:
            self.users[user_id]['cart'][product_name] -= quantity
            self.products[product_name]['stock'] += quantity

    def checkout(self, user_id):
        if user_id not in self.users or not self.users[user_id]['cart']:
            return None

        cart = self.users[user_id]['cart']
        for product_name in cart:
            if product_name not in self.products or self.products[product_name]['price'] < 0:
                return None

        total_price = 0.0
        price_snapshot = {}
        for product_name, quantity in cart.items():
            price_snapshot[product_name] = self.products[product_name]['price']
            total_price += quantity * self.products[product_name]['price']

        order_id = f"SK{self.next_order_id:05d}"
        self.orders[order_id] = {
            'status': 'pending',
            'items': cart.copy(),
            'price_snapshot': price_snapshot,
            'user_id': user_id
        }
        self.users[user_id]['cart'].clear()
        self.next_order_id += 1

        return order_id

    def update_order_status(self, order_id: str, new_status: str) -> None:
        if order_id not in self.orders:
            return

        order = self.orders[order_id]
        current_status = order['status']

        if current_status == 'cancelled':
            return

        valid_transitions = {
            'pending': ['processing', 'cancelled'],
            'processing': ['completed', 'cancelled'],
            'completed': ['shipped', 'cancelled'],
            'shipped': ['delivered', 'cancelled'],
            'delivered': ['cancelled'],
            'cancelled': []
        }

        if new_status not in valid_transitions.get(current_status, []):
            return

        order['status'] = new_status

        if new_status == 'cancelled':
            for product_name, quantity in order['items'].items():
                if product_name in self.products:
                    self.products[product_name]['stock'] += quantity
                else:
                    price = order['price_snapshot'].get(product_name, 0.0)
                    if price < 0:
                        price = 0.0
                    self.products[product_name] = {
                        'price': price,
                        'stock': quantity
                    }

    def get_system_state(self):
        return {
            "users": {k: v.copy() for k, v in self.users.items()},
            "products": {k: v.copy() for k, v in self.products.items()},
            "orders": {k: v.copy() for k, v in self.orders.items()}
        }

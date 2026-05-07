import threading

class EShopSystem:
    def __init__(self):
        self.users = {}
        self.products = {}
        self.orders = {}
        self.next_order_id = 1
        self.order_status_sequence = {
            'pending': ['processing', 'cancelled'],
            'processing': ['completed', 'cancelled'],
            'completed': ['shipped', 'cancelled'],
            'shipped': ['delivered', 'cancelled'],
            'delivered': ['cancelled'],
            'cancelled': []
        }
        self.lock = threading.Lock()

    def create_user(self, user_id):
        if user_id in self.users:
            return False

        self.users[user_id] = {
            'cart': {},
            'reservations': {}
        }
        return True

    def delete_user(self, user_id):
        if user_id not in self.users:
            return False
        user_data = self.users[user_id]
        reservations = user_data['reservations']
        for product_name, quantity in reservations.items():
            if product_name in self.products:
                self.products[product_name]['stock'] += quantity
        del self.users[user_id]
        return True

    def add_product(self, name, price, stock):
        if not name or price < 0 or stock < 0:
            return False

        if name in self.products:
            self.products[name]['price'] = price
            self.products[name]['stock'] += stock
        else:
            self.products[name] = {
                'price': price,
                'stock': stock
            }

        return True

    def delete_product(self, name):
        if name not in self.products:
            return False

        del self.products[name]
        return True

    def modify_cart(self, user_id, product_name, quantity, action):
        if user_id not in self.users:
            return False

        if action == 'add':
            if quantity <= 0:
                return False

            if product_name not in self.products:
                return False

            if quantity > self.products[product_name]['stock']:
                return False

            if product_name in self.users[user_id]['cart']:
                self.users[user_id]['cart'][product_name] += quantity
            else:
                self.users[user_id]['cart'][product_name] = quantity

            if product_name in self.users[user_id]['reservations']:
                self.users[user_id]['reservations'][product_name] += quantity
            else:
                self.users[user_id]['reservations'][product_name] = quantity

            self.products[product_name]['stock'] -= quantity
            return True

        elif action == 'remove':
            if product_name not in self.users[user_id]['cart'] or quantity <= 0:
                return False

            if quantity > self.users[user_id]['cart'][product_name]:
                return False

            if product_name not in self.products:
                return False

            self.users[user_id]['cart'][product_name] -= quantity

            if self.users[user_id]['cart'][product_name] == 0:
                del self.users[user_id]['cart'][product_name]

            if product_name in self.users[user_id]['reservations']:
                self.users[user_id]['reservations'][product_name] -= quantity
                if self.users[user_id]['reservations'][product_name] == 0:
                    del self.users[user_id]['reservations'][product_name]

            self.products[product_name]['stock'] += quantity
            return True

        return False

    def checkout(self, user_id):
        if user_id not in self.users:
            return None

        cart = self.users[user_id]['cart']
        if not cart:
            return None

        for product_name in cart:
            if product_name not in self.products:
                return None

        reservations = self.users[user_id]['reservations']
        for product_name in cart:
            if product_name not in reservations or reservations[product_name] != cart[product_name]:
                return None

        price_snapshot = {}
        total_price = 0.0
        for product_name, quantity in cart.items():
            price = self.products[product_name]['price']
            price_snapshot[product_name] = price
            total_price += price * quantity

        with self.lock:
            order_id = f"SK{self.next_order_id:05d}"
            self.next_order_id += 1

        self.orders[order_id] = {
            'user_id': user_id,
            'products': [{'name': name, 'quantity': qty} for name, qty in cart.items()],
            'status': 'pending',
            'price_snapshot': price_snapshot
        }

        self.users[user_id]['cart'] = {}
        self.users[user_id]['reservations'] = {}

        return order_id

    def update_order_status(self, order_id, new_status):
        if order_id not in self.orders:
            return False

        current_status = self.orders[order_id]['status']

        if current_status == 'cancelled':
            return False

        if new_status not in self.order_status_sequence.get(current_status, []):
            return False

        if current_status == 'delivered' and new_status != 'cancelled':
            return False

        if new_status == 'cancelled':
            for product in self.orders[order_id]['products']:
                product_name = product['name']
                quantity = product['quantity']
                if product_name in self.products:
                    self.products[product_name]['stock'] += quantity
                else:
                    price = self.orders[order_id]['price_snapshot'].get(product_name, 0.0)
                    if price > 0:
                        self.products[product_name] = {
                            'price': price,
                            'stock': quantity
                        }

        self.orders[order_id]['status'] = new_status
        return True

    def get_system_state(self):
        with self.lock:
            state = {
                'users': {k: v.copy() for k, v in self.users.items()},
                'products': self.products.copy(),
                'orders': {k: v.copy() for k, v in self.orders.items()}
            }
        return state
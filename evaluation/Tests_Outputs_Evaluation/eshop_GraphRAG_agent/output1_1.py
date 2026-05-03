import threading


class EShopSystem:
    def __init__(self):
        self.users = {}
        self.products = {}
        self.carts = {}
        self.reservations = {}
        self.orders = {}
        self.next_order_sequence = 1
        self.lock = threading.Lock()

    def create_user(self, user_id: str) -> None:
        if user_id not in self.users:
            self.users[user_id] = {}
            self.carts[user_id] = {}
            self.reservations[user_id] = {}

    def delete_user(self, user_id: str) -> None:
        if user_id not in self.users:
            return

        if user_id in self.reservations:
            for product_name, quantity in self.reservations[user_id].items():
                if product_name in self.products:
                    self.products[product_name]['available_stock'] += quantity
            del self.reservations[user_id]

        if user_id in self.carts:
            del self.carts[user_id]

        del self.users[user_id]

    def add_or_update_product(self, name: str, price: float, stock: int) -> None:
        if not name or price < 0 or stock < 0:
            return

        if name in self.products:
            product = self.products[name]
            product['price'] = price
            product['total_stock'] = stock
            product['available_stock'] = stock
        else:
            self.products[name] = {
                'price': price,
                'total_stock': stock,
                'available_stock': stock
            }

    def delete_product(self, name: str) -> None:
        if name in self.products:
            del self.products[name]

    def add_to_cart(self, user_id: str, product_name: str, quantity: int) -> None:
        if (user_id not in self.users or
            product_name not in self.products or
            quantity <= 0):
            return

        if self.products[product_name]['available_stock'] < quantity:
            return

        if user_id not in self.carts:
            self.carts[user_id] = {}
        if user_id not in self.reservations:
            self.reservations[user_id] = {}

        if product_name in self.carts[user_id]:
            self.carts[user_id][product_name] += quantity
        else:
            self.carts[user_id][product_name] = quantity

        if product_name in self.reservations[user_id]:
            self.reservations[user_id][product_name] += quantity
        else:
            self.reservations[user_id][product_name] = quantity

        self.products[product_name]['available_stock'] -= quantity

    def remove_from_cart(self, user_id: str, product_name: str, quantity: int) -> None:
        product_exists_in_stock = product_name in self.products

        if (user_id not in self.users or
            product_name not in self.carts.get(user_id, {}) or
            quantity <= 0 or
            self.carts[user_id][product_name] < quantity):
            return

        if (user_id in self.reservations and
            product_name in self.reservations[user_id] and
            self.reservations[user_id][product_name] >= quantity):
            if self.reservations[user_id][product_name] == quantity:
                del self.reservations[user_id][product_name]
            else:
                self.reservations[user_id][product_name] -= quantity

        if self.carts[user_id][product_name] == quantity:
            del self.carts[user_id][product_name]
        else:
            self.carts[user_id][product_name] -= quantity

        if product_exists_in_stock:
            self.products[product_name]['available_stock'] += quantity

    def perform_checkout(self, user_id: str) -> str:
        if user_id not in self.users or user_id not in self.carts or not self.carts[user_id]:
            return None

        # Validate all reserved products exist in stock
        for product_name in self.carts[user_id]:
            if product_name not in self.products:
                return None

        order_total = 0.0
        price_snapshot = {}
        for product_name, quantity in self.carts[user_id].items():
            order_total += self.products[product_name]['price'] * quantity
            price_snapshot[product_name] = self.products[product_name]['price']

        with self.lock:
            order_id = f"SK{self.next_order_sequence:05d}"
            self.next_order_sequence += 1

            order_data = {
                'status': 'pending',
                'products': self.carts[user_id].copy(),
                'price_snapshot': price_snapshot,
                'total': order_total,
                'user_id': user_id
            }

            cart_backup = self.carts[user_id].copy()
            reservations_backup = self.reservations.get(user_id, {}).copy()

            try:
                self.carts[user_id].clear()
                if user_id in self.reservations:
                    self.reservations[user_id].clear()

                self.orders[order_id] = order_data
                return order_id
            except:
                self.carts[user_id] = cart_backup
                if user_id in self.reservations:
                    self.reservations[user_id] = reservations_backup
                return None

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

        if new_status not in valid_transitions[current_status]:
            return

        if new_status == 'cancelled':
            for product_name, quantity in order['products'].items():
                if product_name in self.products:
                    self.products[product_name]['available_stock'] += quantity
                else:
                    price_snapshot = order['price_snapshot'][product_name]
                    self.products[product_name] = {
                        'price': price_snapshot,
                        'total_stock': quantity,
                        'available_stock': quantity
                    }

        order['status'] = new_status

    def get_system_state(self) -> dict:
        return {
            "users": self.users,
            "products": {name: {"price": data["price"], "total_stock": data["total_stock"], "available_stock": data["available_stock"]}
                       for name, data in self.products.items()},
            "carts": self.carts,
            "reservations": self.reservations,
            "orders": self.orders,
            "next_order_sequence": self.next_order_sequence
        }
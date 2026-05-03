class EShopSystem:
    def __init__(self):
        self.users = {}
        self.products = {}
        self.available_stock = {}
        self.orders = {}
        self.next_order_id = 1
        self.reservations = {}

    def create_user(self, user_id):
        if not user_id or user_id in self.users:
            return False

        self.users[user_id] = {
            'cart': {},
            'details': {}
        }
        self.reservations[user_id] = {}
        return True

    def delete_user(self, user_id):
        if user_id not in self.users:
            return False

        if user_id in self.reservations:
            for product_name, quantity in self.reservations[user_id].items():
                if product_name in self.available_stock:
                    self.available_stock[product_name] += quantity
            del self.reservations[user_id]

        if 'cart' in self.users[user_id]:
            del self.users[user_id]['cart']

        del self.users[user_id]
        return True

    def add_or_update_product(self, name, price, stock):
        if not name or price < 0 or stock < 0:
            return False

        if name in self.products:
            self.products[name]['price'] = price
            self.products[name]['total_stock'] += stock
            self.available_stock[name] += stock
        else:
            self.products[name] = {
                'price': price,
                'total_stock': stock
            }
            self.available_stock[name] = stock

        return True

    def delete_product(self, name):
        if name not in self.products:
            return False

        if name in self.available_stock:
            del self.available_stock[name]

        del self.products[name]
        return True

    def add_to_cart(self, user_id, product_name, quantity):
        if user_id not in self.users:
            return False

        if product_name not in self.products or quantity <= 0:
            return False

        if product_name not in self.available_stock or self.available_stock[product_name] < quantity:
            return False

        if product_name in self.users[user_id]['cart']:
            self.users[user_id]['cart'][product_name] += quantity
        else:
            self.users[user_id]['cart'][product_name] = quantity

        if product_name in self.reservations[user_id]:
            self.reservations[user_id][product_name] += quantity
        else:
            self.reservations[user_id][product_name] = quantity

        self.available_stock[product_name] -= quantity
        return True

    def remove_from_cart(self, user_id, product_name, quantity):
        if quantity <= 0:
            return False

        if user_id not in self.users:
            return False

        if product_name not in self.products:
            return False

        user_cart = self.users[user_id].get('cart', {})
        if product_name not in user_cart or user_cart[product_name] < quantity:
            return False

        if user_cart[product_name] == quantity:
            del user_cart[product_name]
        else:
            user_cart[product_name] -= quantity

        if user_id in self.reservations:
            if product_name in self.reservations[user_id]:
                if self.reservations[user_id][product_name] == quantity:
                    del self.reservations[user_id][product_name]
                else:
                    self.reservations[user_id][product_name] -= quantity

        if product_name in self.available_stock:
            self.available_stock[product_name] += quantity

        return True

    def checkout(self, user_id):
        if user_id not in self.users or not self.users[user_id]['cart']:
            return False, None

        for product_name in self.users[user_id]['cart']:
            if product_name not in self.products:
                return False, None

        total_price = 0.0
        for product_name, quantity in self.users[user_id]['cart'].items():
            total_price += self.products[product_name]['price'] * quantity

        original_cart = self.users[user_id]['cart'].copy()
        original_reservations = self.reservations.get(user_id, {}).copy()
        original_available_stock = {}
        for product_name in original_reservations:
            original_available_stock[product_name] = self.available_stock.get(product_name, 0)

        original_next_order_id = self.next_order_id

        try:
            order_id = f"SK{self.next_order_id:05d}"
            self.orders[order_id] = {
                'status': 'pending',
                'products': self.users[user_id]['cart'].copy(),
                'price_snapshot': {p: self.products[p]['price'] for p in self.users[user_id]['cart']},
                'total_price': total_price
            }

            self.users[user_id]['cart'].clear()
            if user_id in self.reservations:
                for product_name in self.reservations[user_id]:
                    self.available_stock[product_name] += self.reservations[user_id][product_name]
                del self.reservations[user_id]

            self.next_order_id += 1
            return True, order_id

        except Exception:
            if order_id in self.orders:
                del self.orders[order_id]

            self.users[user_id]['cart'] = original_cart
            if original_reservations:
                self.reservations[user_id] = original_reservations
                for product_name, quantity in original_reservations.items():
                    if product_name in self.available_stock:
                        self.available_stock[product_name] = original_available_stock.get(product_name, 0)

            self.next_order_id = original_next_order_id
            return False, None

    def update_order_status(self, order_id, new_status):
        if order_id not in self.orders:
            return False

        order = self.orders[order_id]
        current_status = order['status']

        if new_status == 'cancelled':
            if current_status in ['cancelled', 'delivered']:
                return False

            order['status'] = 'cancelled'

            for product_name, quantity in order['products'].items():
                if product_name in self.products:
                    if product_name not in self.available_stock:
                        self.available_stock[product_name] = 0
                    self.available_stock[product_name] += quantity
                else:
                    try:
                        if not product_name or order['price_snapshot'][product_name] < 0 or quantity < 0:
                            raise ValueError("Invalid product recreation parameters")
                        if not self.add_or_update_product(
                            name=product_name,
                            price=order['price_snapshot'][product_name],
                            stock=quantity
                        ):
                            raise ValueError("Failed to recreate product")
                    except Exception as e:
                        print(f"Error recreating product {product_name}: {str(e)}")
                        continue

            return True

        valid_transitions = {
            'pending': ['processing'],
            'processing': ['completed'],
            'completed': ['shipped'],
            'shipped': ['delivered']
        }

        if (current_status in valid_transitions and
            new_status in valid_transitions[current_status] and
            current_status not in ['cancelled', 'delivered']):

            order['status'] = new_status
            return True

        return False

    def get_system_state(self, entity_type):
        if entity_type == 'users':
            return {user_id: user_data.copy() for user_id, user_data in self.users.items()}
        elif entity_type == 'products':
            return self.products.copy()
        elif entity_type == 'stock':
            return self.available_stock.copy()
        elif entity_type == 'carts':
            carts = {}
            for user_id, user_data in self.users.items():
                carts[user_id] = user_data.get('cart', {}).copy()
            return carts
        elif entity_type == 'orders':
            return self.orders.copy()
        else:
            return {}
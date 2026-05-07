from copy import deepcopy

from types import MappingProxyType

class EShopSystem:
    def __init__(self):
        self.users = {}
        self.products = {}
        self.orders = {}
        self.next_order_id = 1
        self.reservations = {}

    def create_user(self, user_id):
        if not user_id or user_id in self.users:
            return False

        self.users[user_id] = {
            'cart': {},
            'reservations': {}
        }
        return True

    def add_product(self, product_name, price, stock):
        if not product_name or price < 0 or stock < 0:
            return False

        if product_name in self.products:
            self.products[product_name]['stock'] += stock
            self.products[product_name]['price'] = price
        else:
            self.products[product_name] = {
                'price': price,
                'stock': stock
            }

        return True

    def delete_product(self, product_name):
        if product_name not in self.products:
            return False

        del self.products[product_name]
        return True

    def get_system_state(self):
        """Retrieves the current system state, including users, products, physical stock, carts, and orders.

        Returns:
            dict: A read-only snapshot of the current system state, including:
                - users: Dictionary of user data including carts
                - products: Dictionary of product data including physical stock (reservations are not subtracted)
                - reservations: Dictionary of user reservations
                - orders: Dictionary of all orders
                - next_order_id: The next available order ID
        """
        state = {
            'users': deepcopy(self.users),
            'products': deepcopy(self.products),
            'orders': deepcopy(self.orders),
            'next_order_id': self.next_order_id,
            'reservations': deepcopy(self.reservations)
        }
        return MappingProxyType(state)

    def delete_user(self, user_id):
        if user_id not in self.users:
            return False

        # Process reservations
        user_reservations = self.users[user_id]['reservations'].copy()
        for product_name, quantity in user_reservations.items():
            if product_name in self.products:
                self.products[product_name]['stock'] += quantity
            del self.users[user_id]['reservations'][product_name]

        # Clear cart and reservations
        self.users[user_id]['cart'].clear()

        # Delete user
        del self.users[user_id]

        return True

    def add_to_cart(self, user_id, product_name, quantity):
        if quantity <= 0:
            return False

        if user_id not in self.users:
            return False

        if product_name not in self.products:
            return False

        physical_stock = self.products[product_name]['stock']
        existing_reservations = sum(
            self.users[uid]['reservations'].get(product_name, 0)
            for uid in self.users
            if product_name in self.users[uid]['reservations']
        )

        if quantity > (physical_stock - existing_reservations):
            return False

        if product_name in self.users[user_id]['cart']:
            self.users[user_id]['cart'][product_name] += quantity
        else:
            self.users[user_id]['cart'][product_name] = quantity

        if product_name in self.users[user_id]['reservations']:
            self.users[user_id]['reservations'][product_name] += quantity
        else:
            self.users[user_id]['reservations'][product_name] = quantity

        return True

    def remove_from_cart(self, user_id, product_name, quantity):
        if user_id not in self.users:
            return False

        user_cart = self.users[user_id]['cart']
        if product_name not in user_cart:
            return False

        reserved_quantity = user_cart[product_name]
        if quantity > reserved_quantity:
            return False

        if quantity == reserved_quantity:
            del user_cart[product_name]
        else:
            user_cart[product_name] -= quantity

        user_reservations = self.users[user_id]['reservations']
        if product_name in user_reservations:
            if quantity == user_reservations[product_name]:
                del user_reservations[product_name]
            else:
                user_reservations[product_name] -= quantity

        return True

    def checkout(self, user_id):
        if user_id not in self.users or not self.users[user_id]['cart']:
            return None

        cart = self.users[user_id]['cart']
        total_price = 0.0

        for product_name, quantity in cart.items():
            if product_name not in self.products:
                return None

            product = self.products[product_name]
            other_reservations = sum(
                self.users.get(other_user, {}).get('reservations', {}).get(product_name, 0)
                for other_user in self.users
                if other_user != user_id
            )
            available_stock = product['stock'] - other_reservations

            if available_stock < quantity:
                return None

            total_price += product['price'] * quantity

        order_id = f"SK{self.next_order_id:05d}"
        self.next_order_id += 1

        order = {
            'status': 'pending',
            'items': cart.copy(),
            'price_snapshot': {product: self.products[product]['price'] for product in cart},
            'total_price': total_price
        }
        self.orders[order_id] = order

        for product_name, quantity in cart.items():
            self.products[product_name]['stock'] -= quantity

        self.users[user_id]['cart'].clear()
        if user_id in self.users and 'reservations' in self.users[user_id]:
            self.users[user_id]['reservations'].clear()

        return order_id

    def update_order_status(self, order_id, new_status):
        if order_id not in self.orders:
            return False

        current_status = self.orders[order_id]['status']

        if current_status in ['cancelled', 'delivered']:
            if new_status != 'cancelled':
                return False

        valid_transitions = {
            'pending': ['processing', 'cancelled'],
            'processing': ['completed', 'cancelled'],
            'completed': ['shipped', 'cancelled'],
            'shipped': ['delivered', 'cancelled']
        }

        if new_status not in valid_transitions.get(current_status, []):
            return False

        if new_status == 'cancelled':
            for product_name, quantity in self.orders[order_id]['items'].items():
                if product_name in self.products:
                    self.products[product_name]['stock'] += quantity
                else:
                    price = self.orders[order_id]['price_snapshot'].get(product_name, 0.0)
                    self.products[product_name] = {
                        'price': price,
                        'stock': quantity
                    }

        self.orders[order_id]['status'] = new_status
        return True
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
        """Retrieves the current system state, including users, products, stock, carts, and orders.

        Returns:
            dict: A read-only snapshot of the current system state containing:
                - users: Dictionary of user data including carts and reservations
                - products: Dictionary of product data including price and stock
                - orders: Dictionary of order data including status, items, and price snapshot
                - next_order_id: Current next order ID counter
                - reservations: Dictionary of product reservations by user
        """
        from copy import deepcopy
        from types import MappingProxyType

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
        reservations = self.users[user_id].get('reservations', {})
        for product_name, quantity in reservations.items():
            if product_name in self.products:
                self.products[product_name]['stock'] += quantity

        # Remove user from reservations tracking
        if user_id in self.reservations:
            del self.reservations[user_id]

        # Remove user
        del self.users[user_id]

        return True

    def add_to_cart(self, user_id, product_name, quantity):
        # Validate inputs
        if quantity <= 0:
            return False

        # Check if user exists
        if user_id not in self.users:
            return False

        # Check if product exists
        if product_name not in self.products:
            return False

        product = self.products[product_name]
        available_stock = product['stock']

        # Calculate total reserved quantity for this product across all users
        total_reserved = 0
        for user_reservations in self.reservations.values():
            if product_name in user_reservations:
                total_reserved += user_reservations[product_name]

        # Calculate total quantity including existing cart items
        if product_name in self.users[user_id]['cart']:
            current_quantity = self.users[user_id]['cart'][product_name]
            total_quantity = current_quantity + quantity
        else:
            total_quantity = quantity

        # Check if sufficient stock is available (considering all reservations)
        if total_quantity > (available_stock - total_reserved):
            return False

        # Update user's cart
        if product_name in self.users[user_id]['cart']:
            self.users[user_id]['cart'][product_name] += quantity
        else:
            self.users[user_id]['cart'][product_name] = quantity

        # Deduct from available stock
        self.products[product_name]['stock'] -= quantity

        # Update user's reservation
        if user_id in self.reservations:
            if product_name in self.reservations[user_id]:
                self.reservations[user_id][product_name] += quantity
            else:
                self.reservations[user_id][product_name] = quantity
        else:
            self.reservations[user_id] = {product_name: quantity}

        # Update user's reservations to match global reservations
        if 'reservations' not in self.users[user_id]:
            self.users[user_id]['reservations'] = {}
        self.users[user_id]['reservations'][product_name] = self.reservations[user_id][product_name]

        return True

    def remove_from_cart(self, user_id, product_name, quantity):
        # Validate user exists and product is in cart with sufficient quantity
        if user_id not in self.users or product_name not in self.users[user_id]['cart']:
            return False

        if quantity <= 0 or self.users[user_id]['cart'][product_name] < quantity:
            return False

        # Check if product exists in stock
        product_exists = product_name in self.products

        # Return quantity to stock if product exists
        if product_exists:
            self.products[product_name]['stock'] += quantity

        # Update user's cart
        if self.users[user_id]['cart'][product_name] == quantity:
            del self.users[user_id]['cart'][product_name]
        else:
            self.users[user_id]['cart'][product_name] -= quantity

        # Update global reservations
        if user_id in self.reservations and product_name in self.reservations[user_id]:
            if self.reservations[user_id][product_name] == quantity:
                del self.reservations[user_id][product_name]
                if not self.reservations[user_id]:  # Clean up empty reservations entry
                    del self.reservations[user_id]
            else:
                self.reservations[user_id][product_name] -= quantity

        # Update user's reservations to match global reservations
        if user_id in self.reservations and product_name in self.reservations[user_id]:
            if 'reservations' not in self.users[user_id]:
                self.users[user_id]['reservations'] = {}
            self.users[user_id]['reservations'][product_name] = self.reservations[user_id][product_name]
        else:
            if 'reservations' in self.users[user_id] and product_name in self.users[user_id]['reservations']:
                del self.users[user_id]['reservations'][product_name]
                if not self.users[user_id]['reservations']:
                    del self.users[user_id]['reservations']

        return True

    def checkout(self, user_id):
        # Step 1: Validate user exists and has non-empty cart
        if user_id not in self.users or not self.users[user_id]['cart']:
            return None

        cart = self.users[user_id]['cart']
        price_snapshot = {}
        total_price = 0.0

        # Step 2: Validate all reserved products still exist in the stock system
        for product_name in cart.keys():
            if product_name not in self.products:
                return None

        # Step 3: Validate all reserved products have sufficient stock
        for product_name, quantity in cart.items():
            if self.products[product_name]['stock'] < quantity:
                return None

            # Step 4: Calculate total price using current prices
            price_snapshot[product_name] = self.products[product_name]['price']
            total_price += self.products[product_name]['price'] * quantity

        # Step 5: Generate unique sequential order ID
        order_id = f"SK{self.next_order_id:05d}"

        # Step 6: Create order with status 'pending'
        order_data = {
            'status': 'pending',
            'items': cart.copy(),
            'price_snapshot': price_snapshot,
            'total_price': total_price
        }

        # Step 7: Clear user's cart and reservations
        self.users[user_id]['cart'].clear()
        if 'reservations' in self.users[user_id]:
            self.users[user_id]['reservations'].clear()
        if user_id in self.reservations:
            self.reservations[user_id].clear()

        # Step 8: Add order to orders registry and increment order ID
        self.orders[order_id] = order_data
        self.next_order_id += 1

        return order_id

    def update_order_status(self, order_id, new_status):
        # Validate order exists
        if order_id not in self.orders:
            return False

        current_status = self.orders[order_id]['status']

        # Check if order is already in terminal state
        if current_status in ['cancelled', 'delivered']:
            return False

        # Validate status transition
        valid_transitions = {
            'pending': ['processing', 'cancelled'],
            'processing': ['completed', 'cancelled'],
            'completed': ['shipped', 'cancelled'],
            'shipped': ['delivered', 'cancelled'],
            'delivered': ['cancelled']
        }

        # Check if the transition is valid
        if new_status not in valid_transitions.get(current_status, []):
            return False

        # Handle cancellation
        if new_status == 'cancelled':
            for product_name, quantity in self.orders[order_id]['items'].items():
                if product_name in self.products:
                    # Restore stock if product exists
                    self.products[product_name]['stock'] += quantity
                else:
                    # Recreate product with price from order snapshot
                    price = self.orders[order_id]['price_snapshot'].get(product_name, 0.0)
                    if price >= 0:  # Ensure price is valid
                        self.products[product_name] = {
                            'price': price,
                            'stock': quantity
                        }

        # Update order status
        self.orders[order_id]['status'] = new_status
        return True
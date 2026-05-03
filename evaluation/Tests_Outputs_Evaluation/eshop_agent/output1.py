import threading

class EShopSystem:
    def __init__(self):
        self.users = {}
        self.products = {}
        self.orders = {}
        self.next_order_id = 1
        self.reservations = {}
        self.lock = threading.Lock()

    def add_product(self, name, price, stock):
        if not name or price < 0 or stock < 0:
            return

        if name in self.products:
            self.products[name]['stock'] += stock
            self.products[name]['price'] = price
        else:
            self.products[name] = {
                'price': price,
                'stock': stock
            }

    def create_user(self, user_id):
        if user_id in self.users:
            print(f"Warning: User ID {user_id} already exists. Request ignored.")
            print(f"Notification: Administrator notified about duplicate user ID {user_id}.")
            return

        self.users[user_id] = {
            'cart': {},
            'reservations': {}
        }

    def delete_user(self, user_id):
        if user_id not in self.users:
            print(f"Warning: User ID {user_id} does not exist. Request ignored.")
            return

        # Clear cart contents
        if 'cart' in self.users[user_id]:
            self.users[user_id]['cart'].clear()

        # Handle reservations and stock adjustments
        if user_id in self.reservations:
            for product_name, quantity in list(self.reservations[user_id].items()):
                if product_name in self.products:
                    self.products[product_name]['stock'] += quantity
            # Remove the user's reservations entry
            del self.reservations[user_id]

        # Delete the user
        del self.users[user_id]

    def delete_product(self, name):
        if name in self.products:
            del self.products[name]

    def modify_cart(self, user_id, product_name, quantity, action):
        # Validate user exists and quantity is positive
        if user_id not in self.users or quantity <= 0:
            return

        # Handle add action
        if action == 'add':
            # Check product exists and has sufficient stock
            if product_name not in self.products or quantity > self.products[product_name]['stock']:
                return

            # Update cart and reservations
            if product_name in self.users[user_id]['cart']:
                self.users[user_id]['cart'][product_name] += quantity
            else:
                self.users[user_id]['cart'][product_name] = quantity

            # Update reservations
            if user_id not in self.reservations:
                self.reservations[user_id] = {}
            if product_name in self.reservations[user_id]:
                self.reservations[user_id][product_name] += quantity
            else:
                self.reservations[user_id][product_name] = quantity

            # Deduct from available stock
            self.products[product_name]['stock'] -= quantity

        # Handle remove action
        elif action == 'remove':
            # Check product exists in cart and has sufficient reserved quantity
            if (product_name not in self.users[user_id]['cart'] or
                quantity > self.users[user_id]['cart'][product_name]):
                return

            # Check product still exists in stock system
            if product_name not in self.products:
                return

            # Update cart
            self.users[user_id]['cart'][product_name] -= quantity
            if self.users[user_id]['cart'][product_name] == 0:
                del self.users[user_id]['cart'][product_name]

            # Update reservations
            if user_id in self.reservations and product_name in self.reservations[user_id]:
                self.reservations[user_id][product_name] -= quantity
                if self.reservations[user_id][product_name] == 0:
                    del self.reservations[user_id][product_name]
                    if not self.reservations[user_id]:
                        del self.reservations[user_id]

            # Return stock to available if product exists
            self.products[product_name]['stock'] += quantity

    def perform_checkout(self, user_id):
        # Step 1: Validate user exists and cart is not empty
        if user_id not in self.users or not self.users[user_id]['cart']:
            print(f"Warning: User ID {user_id} does not exist or cart is empty. Checkout failed.")
            return None

        cart = self.users[user_id]['cart']
        total_price = 0.0
        order_products = {}

        # Step 2: Validate all reserved products still exist and calculate total price
        for product_name, quantity in cart.items():
            if product_name not in self.products:
                # Revert all changes and notify user
                for p, q in cart.items():
                    if p in self.products:
                        self.products[p]['stock'] += q
                if user_id in self.reservations:
                    del self.reservations[user_id]
                print(f"Warning: Product {product_name} no longer exists. Checkout failed.")
                return None

            total_price += self.products[product_name]['price'] * quantity
            order_products[product_name] = {
                'quantity': quantity,
                'price': self.products[product_name]['price']
            }

        # Step 3: Generate unique order ID atomically
        with self.lock:
            order_id = f"SK{self.next_order_id:05d}"
            self.next_order_id += 1

        # Store original state for potential rollback
        original_stock = {p: self.products[p]['stock'] for p in cart if p in self.products}
        original_reservations = self.reservations.get(user_id, {}).copy()

        try:
            # Step 4: Create order
            self.orders[order_id] = {
                'status': 'pending',
                'products': order_products,
                'total_price': total_price
            }

            # Step 5: Clear cart and reservations
            self.users[user_id]['cart'].clear()
            if user_id in self.reservations:
                del self.reservations[user_id]

            return order_id
        except:
            # Revert all changes if order creation fails
            for p, q in cart.items():
                if p in self.products:
                    self.products[p]['stock'] = original_stock.get(p, self.products[p]['stock'])
            if user_id in self.reservations:
                self.reservations[user_id] = original_reservations
            print(f"Warning: Checkout failed for user {user_id}. All changes reverted.")
            return None

    def update_order_status(self, order_id, new_status):
        # Validate order exists and status transition is allowed
        if order_id not in self.orders:
            return

        order = self.orders[order_id]
        current_status = order['status']

        # Check if current status is 'cancelled' (terminal state)
        if current_status == 'cancelled':
            return

        # Validate status transition
        valid_transitions = {
            'pending': ['processing', 'cancelled'],
            'processing': ['completed', 'cancelled'],
            'completed': ['shipped', 'cancelled'],
            'shipped': ['delivered', 'cancelled'],
            'delivered': ['cancelled']
        }

        if new_status not in valid_transitions.get(current_status, []):
            return

        # Handle cancellation
        if new_status == 'cancelled':
            for product_name, product_data in order['products'].items():
                quantity = product_data['quantity']

                if product_name in self.products:
                    # Return stock to available stock
                    self.products[product_name]['stock'] += quantity
                else:
                    # Recreate product with price from order snapshot
                    self.products[product_name] = {
                        'price': product_data['price'],
                        'stock': quantity
                    }

        # Update order status
        order['status'] = new_status

    def get_system_state(self):
        # Compile users state including carts and reservations
        users_state = {
            user_id: {
                'cart': self.users[user_id]['cart'],
                'reservations': self.reservations.get(user_id, {})
            }
            for user_id in self.users
        }

        # Compile products state including available stock (stock not reserved in any cart)
        products_state = {
            product_name: {
                'price': self.products[product_name]['price'],
                'available_stock': self.products[product_name]['stock']
            }
            for product_name in self.products
        }

        # Compile orders state
        orders_state = {
            order_id: {
                'status': self.orders[order_id]['status'],
                'products': self.orders[order_id]['products'],
                'total_price': self.orders[order_id]['total_price']
            }
            for order_id in self.orders
        }

        # Return compiled state
        return {
            'users': users_state,
            'products': products_state,
            'available_stock': {p: d['available_stock'] for p, d in products_state.items()},
            'carts': {u: d['cart'] for u, d in users_state.items()},
            'reservations': {u: d['reservations'] for u, d in users_state.items()},
            'orders': orders_state
        }
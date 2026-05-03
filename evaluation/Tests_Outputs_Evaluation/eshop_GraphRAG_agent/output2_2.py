import threading

class User:
    def __init__(self, user_id):
        self.user_id = user_id
        self.cart = {}


class Product:
    def __init__(self, name: str, price: float, stock: int):
        self.name = name
        self.price = price
        self.stock = stock


class Order:
    def __init__(self, order_id: str, user_id: str, products: dict, total_price: float):
        self.order_id = order_id
        self.user_id = user_id
        self.status = 'pending'
        self.products = products
        self.total_price = total_price
        self.valid_transitions = {
            'pending': ['processing', 'cancelled'],
            'processing': ['completed', 'cancelled'],
            'completed': ['shipped', 'cancelled'],
            'shipped': ['delivered', 'cancelled'],
            'delivered': ['cancelled'],
            'cancelled': []
        }

    def is_valid_transition(self, new_status):
        """Checks if a status transition is valid."""
        if self.status in self.valid_transitions and new_status in self.valid_transitions[self.status]:
            return True
        return False
    

class EShopBackend:
    def __init__(self):
        self.users = {}
        self.products = {}
        self.orders = {}
        self.next_order_id = 1
        self.reservations = {}
        self.order_id_prefix = "SK"
        self.order_id_digits = 5
        self.available_stock = {}
        self.lock = threading.Lock()

    def create_user(self, user_id):
        if user_id in self.users:
            return False
        self.users[user_id] = User(user_id)
        return True

    def delete_user(self, user_id: str) -> bool:
        if user_id not in self.users:
            return False

        with self.lock:
            # Get user's reservations
            user_reservations = {}
            for product_name, user_reservation in self.reservations.items():
                if user_id in user_reservation:
                    user_reservations[product_name] = user_reservation[user_id]

            # Process each reservation
            for product_name, quantity in user_reservations.items():
                if product_name in self.products:
                    # Return stock to available_stock if product exists
                    self.available_stock[product_name] += quantity
                # If product doesn't exist, skip stock adjustment (as per specification)

            # Remove user from reservations
            for product_name in user_reservations.keys():
                if product_name in self.reservations and user_id in self.reservations[product_name]:
                    del self.reservations[product_name][user_id]
                    if not self.reservations[product_name]:  # Clean up empty product reservations
                        del self.reservations[product_name]

            # Remove user from users
            del self.users[user_id]

        return True

    def add_product(self, name: str, price: float, stock: int) -> bool:
        if not isinstance(name, str) or price < 0 or stock < 0:
            return False

        with self.lock:
            if name in self.products:
                product = self.products[name]
                product.price = price
                product.stock += stock
                self.available_stock[name] += stock
            else:
                product = Product(name, price, stock)
                self.products[name] = product
                self.available_stock[name] = stock

        return True

    def delete_product(self, name: str) -> bool:
        if name not in self.products:
            return False

        with self.lock:
            # Remove from products and available_stock
            del self.products[name]
            if name in self.available_stock:
                del self.available_stock[name]
            # Preserve reservations for the deleted product
            # (as per Use Case requirement)
        return True

    def modify_cart(self, user_id, product_name, quantity, operation):
        if user_id not in self.users or product_name not in self.products:
            return False

        if operation == 'add':
            if quantity <= 0:
                return False

            with self.lock:
                if product_name not in self.available_stock or self.available_stock[product_name] < quantity:
                    return False

                if product_name not in self.users[user_id].cart:
                    self.users[user_id].cart[product_name] = quantity
                else:
                    self.users[user_id].cart[product_name] += quantity

                if product_name not in self.reservations:
                    self.reservations[product_name] = {}
                if user_id not in self.reservations[product_name]:
                    self.reservations[product_name][user_id] = 0
                self.reservations[product_name][user_id] += quantity

                self.available_stock[product_name] -= quantity
                return True

        elif operation == 'remove':
            if quantity <= 0:
                return False

            with self.lock:
                if product_name not in self.users[user_id].cart:
                    return False

                if self.users[user_id].cart[product_name] < quantity:
                    return False

                if product_name in self.products:
                    if product_name not in self.available_stock:
                        self.available_stock[product_name] = 0
                    self.available_stock[product_name] += quantity
                else:
                    if product_name in self.reservations and user_id in self.reservations[product_name]:
                        del self.reservations[product_name][user_id]
                        if not self.reservations[product_name]:
                            del self.reservations[product_name]

                self.users[user_id].cart[product_name] -= quantity
                if self.users[user_id].cart[product_name] <= 0:
                    del self.users[user_id].cart[product_name]
                return True

        return False

    def perform_checkout(self, user_id):
        # Check if user exists
        if user_id not in self.users:
            return False, None

        # Get user's cart
        cart = self.users[user_id].cart
        if not cart:
            return False, None

        # Acquire lock for thread-safe operations
        with self.lock:
            # Verify all products in cart are available with matching quantities
            for product_name, quantity in cart.items():
                if product_name not in self.reservations or user_id not in self.reservations[product_name]:
                    return False, None
                if self.reservations[product_name][user_id] != quantity:
                    return False, None
                # Verify product still exists in products dictionary
                if product_name not in self.products:
                    return False, None

            # Calculate total price
            total_price = sum(
                self.products[product_name].price * quantity
                for product_name, quantity in cart.items()
            )

            # Generate order ID
            order_id = f"{self.order_id_prefix}{str(self.next_order_id).zfill(self.order_id_digits)}"

            # Create order snapshot
            order_snapshot = {
                product_name: {
                    'quantity': quantity,
                    'price_at_checkout': self.products[product_name].price
                }
                for product_name, quantity in cart.items()
            }

            # Create and store order
            order = Order(
                order_id=order_id,
                user_id=user_id,
                total_price=total_price,
                products=order_snapshot
            )
            self.orders[order_id] = order

            # Clear cart and reservations
            for product_name, quantity in cart.items():
                if product_name in self.reservations and user_id in self.reservations[product_name]:
                    del self.reservations[product_name][user_id]
                    if not self.reservations[product_name]:
                        del self.reservations[product_name]

            # Clear the cart
            self.users[user_id].cart.clear()

            # Increment order ID
            self.next_order_id += 1

        return True, order_id

    def update_order_status(self, order_id: str, new_status: str) -> bool:
        # Check if the order exists
        if order_id not in self.orders:
            return False

        order = self.orders[order_id]
        current_status = order.status

        # Check if transition is from 'cancelled' (explicitly ignore)
        if current_status == 'cancelled':
            return False

        # Use Order's is_valid_transition method for validation
        if not order.is_valid_transition(new_status):
            return False

        # Handle cancellation separately
        if new_status == 'cancelled':
            with self.lock:
                for product_name, item_data in order.products.items():
                    quantity = item_data['quantity']
                    price_at_checkout = item_data['price_at_checkout']

                    if product_name in self.products:
                        # Product exists, increase available stock
                        self.available_stock[product_name] += quantity
                        self.products[product_name].stock += quantity
                    else:
                        # Product doesn't exist, recreate it with order snapshot details
                        self.products[product_name] = Product(product_name, price_at_checkout, quantity)
                        self.available_stock[product_name] = quantity

        # Update the order status
        order.status = new_status
        return True

    def get_system_state(self):
        """Provides access to the current system state.

        Returns:
            dict: Dictionary containing the current system state with keys:
                - 'users': Current users with user IDs and their carts
                - 'products': Current products with names, prices, and available stock
                - 'available_stock': Products not reserved in any cart
                - 'reservations': All current reservations in the system
                - 'orders': All current orders and their statuses
                - 'next_order_id': The next available order ID
        """
        system_state = {
            "users": {user_id: user.cart for user_id, user in self.users.items()},
            "products": {
                name: {
                    "price": product.price,
                    "stock": product.stock
                } for name, product in self.products.items()
            },
            "available_stock": self.available_stock.copy(),
            "reservations": self.reservations.copy(),
            "orders": {
                order_id: {
                    'status': order.status,
                    'products': order.products,
                    'total_price': order.total_price
                } for order_id, order in self.orders.items()
            },
            "next_order_id": self.next_order_id
        }
        return system_state
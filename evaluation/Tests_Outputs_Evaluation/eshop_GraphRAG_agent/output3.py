class EShopBackendSystem:
    def __init__(self):
        self.users = {}
        self.products = {}
        self.carts = {}
        self.orders = {}
        self.next_order_id = 1
        self.order_status_transitions = {
            'pending': ['processing', 'cancelled'],
            'processing': ['completed', 'cancelled'],
            'completed': ['shipped', 'cancelled'],
            'shipped': ['delivered', 'cancelled'],
            'delivered': ['cancelled'],
            'cancelled': []
        }

    def create_user(self, user_id: str) -> bool:
        if not isinstance(user_id, str) or not user_id.strip():
            return False

        if user_id in self.users:
            return False

        self.users[user_id] = {}
        self.carts[user_id] = {}

        return True

    def delete_user(self, user_id: str) -> bool:
        if user_id not in self.users:
            return False

        # Process cart reservations
        if user_id in self.carts:
            for product_name, reserved_quantity in self.carts[user_id].items():
                if product_name in self.products:
                    self.products[product_name]['stock'] += reserved_quantity
            del self.carts[user_id]

        # Delete user but preserve orders
        del self.users[user_id]

        return True

    def add_or_update_product(self, name: str, price: float, stock: int) -> bool:
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

    def delete_product(self, name: str) -> bool:
        if name not in self.products:
            return False

        # Remove the product from available stock
        del self.products[name]

        # Preserve reservations for the product in user carts
        # No need to cancel reservations as per Use Case

        return True

    def modify_cart(self, user_id: str, product_name: str, quantity: int) -> bool:
        # Validate user exists
        if user_id not in self.users:
            return False

        # Validate product exists
        if product_name not in self.products:
            return False

        # Get current product stock
        current_stock = self.products[product_name]['stock']

        # Handle adding to cart (positive quantity)
        if quantity > 0:
            # Check if product is already in cart
            if user_id in self.carts and product_name in self.carts[user_id]:
                # Increase reserved quantity
                new_reserved = self.carts[user_id][product_name] + quantity
                # Check if new reserved quantity is available
                if new_reserved <= current_stock:
                    self.carts[user_id][product_name] = new_reserved
                    self.products[product_name]['stock'] -= quantity
                    return True
                else:
                    return False
            else:
                # New product in cart
                if quantity <= current_stock and quantity > 0:
                    # Initialize cart if needed
                    if user_id not in self.carts:
                        self.carts[user_id] = {}
                    # Add to cart and deduct stock
                    self.carts[user_id][product_name] = quantity
                    self.products[product_name]['stock'] -= quantity
                    return True
                else:
                    return False

        # Handle removing from cart (negative quantity)
        elif quantity < 0:
            # Check if product is in cart
            if user_id in self.carts and product_name in self.carts[user_id]:
                reserved_quantity = self.carts[user_id][product_name]
                remove_quantity = abs(quantity)

                # Validate removal quantity
                if remove_quantity <= reserved_quantity:
                    # Calculate new reserved quantity
                    new_reserved = reserved_quantity - remove_quantity

                    # Return stock if product exists
                    if product_name in self.products:
                        self.products[product_name]['stock'] += remove_quantity

                    # Update cart
                    if new_reserved > 0:
                        self.carts[user_id][product_name] = new_reserved
                    else:
                        del self.carts[user_id][product_name]

                    return True
                else:
                    return False
            else:
                return False

        # Ignore zero quantity
        else:
            return False

    def checkout(self, user_id: str) -> tuple[bool, str]:
        # Validate the cart is not empty
        if user_id not in self.carts or not self.carts[user_id]:
            return False, None

        # Check all reserved products exist and have sufficient reserved quantity
        for product_name, quantity in self.carts[user_id].items():
            if product_name not in self.products or quantity <= 0:
                return False, None

        # Calculate total price using current product prices
        total_price = sum(
            self.products[product_name]['price'] * quantity
            for product_name, quantity in self.carts[user_id].items()
        )

        # Generate a unique sequential order ID
        order_id = f"SK{self.next_order_id:05d}"
        self.next_order_id += 1

        # Create a new order with status 'pending' and snapshotted product prices
        self.orders[order_id] = {
            'status': 'pending',
            'products': {
                product_name: {
                    'quantity': quantity,
                    'price': self.products[product_name]['price']
                }
                for product_name, quantity in self.carts[user_id].items()
            },
            'total_price': total_price,
            'user_id': user_id
        }

        # Clear the cart only after all validations pass
        self.carts[user_id].clear()
        return True, order_id

    def update_order_status(self, order_id: str, new_status: str) -> bool:
        # Check if order exists
        if order_id not in self.orders:
            return False

        current_status = self.orders[order_id]['status']

        # Check if transition is valid
        if new_status == 'cancelled':
            if current_status == 'delivered':
                # Only allow delivered -> cancelled
                pass
            elif current_status == 'cancelled':
                # Ignore transitions from cancelled
                return False
            else:
                # Allow cancelled from any state except delivered
                pass
        else:
            # Check standard transitions
            if new_status not in self.order_status_transitions.get(current_status, []):
                return False

        # Update status
        self.orders[order_id]['status'] = new_status

        # Handle stock adjustments for cancellations
        if new_status == 'cancelled':
            for product_name, product_data in self.orders[order_id]['products'].items():
                quantity = product_data['quantity']
                if product_name in self.products:
                    # Product exists, increase stock
                    self.products[product_name]['stock'] += quantity
                else:
                    # Product doesn't exist, recreate with price from order
                    price = product_data['price']
                    self.products[product_name] = {
                        'price': price,
                        'stock': quantity
                    }

        return True

    def get_system_state(self) -> dict:
        """Returns the current state of users, products, stock, carts, and orders."""
        return {
            "users": self.users,
            "products": self.products,
            "carts": self.carts,
            "orders": self.orders,
            "next_order_id": self.next_order_id,
            "order_status_transitions": self.order_status_transitions
        }

    def validate_system_integrity(self) -> bool:
        is_valid = True

        for product_name, product_data in self.products.items():
            total_reserved = 0

            # Calculate total reserved quantity across all carts
            for cart in self.carts.values():
                if product_name in cart:
                    total_reserved += cart[product_name]

            # Check if reserved quantity exceeds available stock
            if total_reserved > product_data['stock']:
                is_valid = False
                break

        # Validate order status transitions
        for order in self.orders.values():
            current_status = order['status']
            if current_status not in self.order_status_transitions:
                is_valid = False
                break

        # Validate order IDs are unique and sequential
        order_ids = [int(order_id[2:]) for order_id in self.orders.keys()]
        if sorted(order_ids) != list(range(1, len(order_ids) + 1)):
            is_valid = False

        # Validate all reserved products exist in stock
        for cart in self.carts.values():
            for product_name in cart.keys():
                if product_name not in self.products:
                    is_valid = False
                    break

        return is_valid
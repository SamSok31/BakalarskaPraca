from eshop_agent.output3_1 import EShopSystem as GeneratedSystem


class EShopSystem:

    def __init__(self):
        self.system = GeneratedSystem()
        self.order_user_map = {}


    def create_user(self, user_id: str):
        self.system.create_user(user_id)

    def delete_user(self, user_id: str):
        self.system.delete_user(user_id)


    def add_product(self, product_id: str, price: int, stock: int):
        self.system.add_or_update_product(product_id, price, stock)

    def delete_product(self, product_id: str):
        self.system.delete_product(product_id)


    def add_to_cart(self, user_id: str, product_id: str, quantity: int):
        self.system.add_to_cart(user_id, product_id, quantity)

    def remove_from_cart(self, user_id: str, product_id: str, quantity: int):
        self.system.remove_from_cart(user_id, product_id, quantity)


    def checkout(self, user_id: str):
        success, order_id = self.system.checkout(user_id)

        if success and order_id is not None:
            self.order_user_map[order_id] = user_id

    def update_order_status(self, order_id: str, new_status: str):
        self.system.update_order_status(order_id, new_status)


    def get_state(self):
        users = set(self.system.users.keys())

        products = set()
        stock = set()

        for name, product in self.system.products.items():
            products.add((name, int(product["price"])))

        for name, qty in self.system.available_stock.items():
            stock.add((name, int(qty)))

        carts = set()

        for user_id, user_data in self.system.users.items():
            cart = user_data.get("cart", {})

            items = tuple(sorted(
                (name, qty) for name, qty in cart.items() if qty > 0
            ))

            carts.add((user_id, items))

        orders = set()

        for order_id, order in self.system.orders.items():

            items = []
            total = 0

            for name, quantity in order["products"].items():
                price = order["price_snapshot"][name]

                items.append((name, quantity))
                total += price * quantity

            items_tuple = tuple(sorted(items))

            user_id = self.order_user_map.get(order_id, None)

            orders.add((
                order_id,
                order["status"],
                user_id,
                items_tuple,
                int(total)
            ))

        return {
            "users": users,
            "products": products,
            "stock": stock,
            "carts": carts,
            "orders": orders,
        }

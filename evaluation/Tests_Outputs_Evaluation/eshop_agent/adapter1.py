from eshop_agent.output1 import EShopSystem as GeneratedSystem


class EShopSystem:

    def __init__(self):
        self.system = GeneratedSystem()
        self.order_to_user = {}


    def create_user(self, user_id: str):
        self.system.create_user(user_id)

    def delete_user(self, user_id: str):
        self.system.delete_user(user_id)


    def add_product(self, product_id: str, price: int, stock: int):
        self.system.add_product(product_id, price, stock)

    def delete_product(self, product_id: str):
        self.system.delete_product(product_id)


    def add_to_cart(self, user_id: str, product_id: str, quantity: int):
        self.system.modify_cart(user_id, product_id, quantity, "add")

    def remove_from_cart(self, user_id: str, product_id: str, quantity: int):
        self.system.modify_cart(user_id, product_id, quantity, "remove")


    def checkout(self, user_id: str):
        order_id = self.system.perform_checkout(user_id)
        if order_id:
            self.order_to_user[order_id] = user_id

    def update_order_status(self, order_id: str, new_status: str):
        self.system.update_order_status(order_id, new_status)


    def get_state(self):
        state = self.system.get_system_state()

        users = set(state["users"].keys())

        products = set(
            (name, int(data["price"]))
            for name, data in state["products"].items()
        )

        stock = set(
            (name, qty)
            for name, qty in state["available_stock"].items()
        )

        carts = set()
        for u_id, cart in state["carts"].items():
            items = tuple(sorted(
                (p, q) for p, q in cart.items() if q > 0
            ))
            carts.add((u_id, items))

        orders = set()
        for order_id, order in state["orders"].items():

            items = []
            total = 0

            for product_name, data in order["products"].items():
                quantity = data["quantity"]
                price = data["price"]

                items.append((product_name, quantity))
                total += quantity * price

            items_tuple = tuple(sorted(items))

            user_id = self.order_to_user.get(order_id, None)

            orders.add((
                order_id,
                order["status"],
                user_id,
                items_tuple,
                total
            ))

        return {
            "users": users,
            "products": products,
            "stock": stock,
            "carts": carts,
            "orders": orders,
        }

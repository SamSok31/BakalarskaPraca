from eshop_GraphRAG_agent.output1_2 import EShopSystem as EShopBackend


class EShopSystem:

    def __init__(self):
        self.system = EShopBackend()


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
        self.system.perform_checkout(user_id)

    def update_order_status(self, order_id: str, new_status: str):
        self.system.update_order_status(order_id, new_status)


    def get_state(self):
        state = self.system.get_system_state()

        users = set(state["users"].keys())

        products = set()
        stock = set()

        for name, data in state["products"].items():
            products.add((name, int(data["price"])))
            stock.add((name, int(data["available_stock"])))

        carts = set()

        for user_id in users:
            cart_dict = state["carts"].get(user_id, {})

            items = tuple(sorted(
                (product_name, quantity)
                for product_name, quantity in cart_dict.items()
                if quantity > 0
            ))

            carts.add((user_id, items))

        orders = set()

        for order_id, order in state["orders"].items():

            items = tuple(sorted(
                (product_name, quantity)
                for product_name, quantity in order["products"].items()
            ))

            total = int(order["total"])

            orders.add((
                order_id,
                order["status"],
                order["user_id"],
                items,
                total
            ))

        return {
            "users": users,
            "products": products,
            "stock": stock,
            "carts": carts,
            "orders": orders,
        }

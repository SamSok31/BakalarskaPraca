from eshop_GraphRAG_agent.output2_2 import EShopBackend as GeneratedSystem


class EShopSystem:

    def __init__(self):
        self.system = GeneratedSystem()


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

        for name, qty in state["available_stock"].items():
            stock.add((name, int(qty)))

        carts = set()

        for user_id in users:
            cart_dict = state["users"].get(user_id, {})

            items = tuple(sorted(
                (product_name, quantity)
                for product_name, quantity in cart_dict.items()
                if quantity > 0
            ))

            carts.add((user_id, items))

        orders = set()

        for order_id, order in state["orders"].items():

            items = tuple(sorted(
                (product_name, item_data["quantity"])
                for product_name, item_data in order["products"].items()
            ))

            total = int(order["total_price"])

            user_id = None

            if order_id in self.system.orders:
                user_id = self.system.orders[order_id].user_id

            orders.add((
                order_id,
                order["status"],
                user_id,
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

from eshop_LLM.output1_2 import EShopBackend as GeneratedSystem
from eshop_LLM.output1_2 import OrderStatus

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
        self.system.add_to_cart(user_id, product_id, quantity)

    def remove_from_cart(self, user_id: str, product_id: str, quantity: int):
        self.system.remove_from_cart(user_id, product_id, quantity)


    def checkout(self, user_id: str):
        self.system.checkout(user_id)

    def update_order_status(self, order_id: str, new_status: str):
        try:
            enum_status = OrderStatus[new_status.upper()]
        except:
            enum_status = new_status

        self.system.update_order_status(order_id, enum_status)


    def get_state(self):
        state = self.system.get_current_state()

        users = set(state["users"])

        products = set(
            (name, int(data["price"]))
            for name, data in state["products"].items()
        )

        stock = set(
            (name, qty)
            for name, qty in state["available_stock"].items()
        )

        carts = set()
        for user_id in users:
            cart_items = state["carts"].get(user_id, [])
            normalized = tuple(sorted((p, q) for p, q in cart_items if q > 0))
            carts.add((user_id, normalized))

        orders = set()
        for o in state["orders"]:
            order_id = o["order_id"]
            user_id = o["user_id"]
            status = o["status"].lower()

            items = []
            total = 0

            for product_name, (quantity, price) in o["products"]:
                items.append((product_name, quantity))
                total += quantity * price

            items_tuple = tuple(sorted(items))

            orders.add((order_id, status, user_id, items_tuple, total))

        return {
            "users": users,
            "products": products,
            "stock": stock,
            "carts": carts,
            "orders": orders,
        }

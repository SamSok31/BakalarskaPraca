from eshop_LLM.output3_1 import EShopBackend as GeneratedSystem


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
        self.system.update_order_status(order_id, new_status)


    def get_state(self):
        state = self.system.get_state()

        users = set(state["users"].keys())

        products = set(
            (name, int(product.price))
            for name, product in state["products"].items()
        )

        stock = set(
            (name, qty)
            for name, qty in state["available_stock"].items()
        )

        carts = set()
        for user_id, user in state["users"].items():
            items = tuple(sorted(
                (p, q) for p, q in user.cart.items() if q > 0
            ))
            carts.add((user_id, items))

        orders = set()
        for order_id, order in state["orders"].items():

            items = []
            total = 0

            for product_name, (quantity, price) in order.products.items():
                items.append((product_name, quantity))
                total += quantity * price

            items_tuple = tuple(sorted(items))

            orders.add((
                order_id,
                order.status,
                order.user_id,
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

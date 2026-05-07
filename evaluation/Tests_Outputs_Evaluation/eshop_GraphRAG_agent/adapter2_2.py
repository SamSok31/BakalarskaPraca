from eshop_GraphRAG_agent.output2_2 import EShopSystem as GeneratedSystem


class EShopSystem:

    def __init__(self):
        self.system = GeneratedSystem()


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
        return self.system.checkout(user_id)

    def update_order_status(self, order_id: str, new_status: str):
        self.system.update_order_status(order_id, new_status)


    def get_state(self):
        state = self.system.get_system_state()

        users = set()
        carts = set()
        products = set()
        stock = set()
        orders = set()


        for user_id, user_data in state["users"].items():
            users.add(user_id)

            cart_items = tuple(sorted(user_data.get("cart", {}).items()))
            carts.add((user_id, cart_items))


        for product_id, product_data in state["products"].items():
            price = product_data.get("price", 0)
            current_stock = product_data.get("stock", 0)

            products.add((product_id, price))
            stock.add((product_id, current_stock))


        for order_id, order_data in state["orders"].items():
            user_id = order_data.get("user_id")
            status = order_data.get("status")
            items = tuple(sorted(order_data.get("items", {}).items()))

            total_price = 0
            price_snapshot = order_data.get("price_snapshot", {})

            for product_id, quantity in items:
                price = price_snapshot.get(product_id, 0)
                total_price += price * quantity

            orders.add((order_id, status, user_id, items, total_price))

        return {
            "users": users,
            "products": products,
            "stock": stock,
            "carts": carts,
            "orders": orders,
        }

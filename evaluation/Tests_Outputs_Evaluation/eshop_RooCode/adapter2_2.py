from eshop_RooCode.output2_2 import EShop as GeneratedSystem
from eshop_RooCode.output2_2 import OrderStatus


class EShopSystem:

    def __init__(self):
        self.system = GeneratedSystem()


    def create_user(self, user_id: str):
        self.system.create_user(user_id)

    def delete_user(self, user_id: str):
        self.system.delete_user(user_id)


    def add_product(self, product_id: str, price: int, stock: int):
        self.system.add_product(product_id, product_id, price, stock)

    def delete_product(self, product_id: str):
        self.system.delete_product(product_id)


    def add_to_cart(self, user_id: str, product_id: str, quantity: int):
        self.system.modify_cart(user_id, product_id, quantity)

    def remove_from_cart(self, user_id: str, product_id: str, quantity: int):
        self.system.modify_cart(user_id, product_id, -quantity)


    def checkout(self, user_id: str):
        self.system.checkout(user_id)

    def update_order_status(self, order_id: str, new_status: str):
        try:
            status = OrderStatus(new_status.lower())
        except Exception:
            return
        self.system.update_order_status(order_id, status)


    def get_state(self):
        users = set(self.system.get_users())

        products = set()
        stock = set()

        product_data = self.system.get_products()
        stock_data = self.system.get_available_stock()

        for pid, pdata in product_data.items():
            products.add((pdata["name"], int(pdata["price"])))

        for pid, qty in stock_data.items():
            name = product_data[pid]["name"]
            stock.add((name, int(qty)))

        carts = set()

        for user_id in users:
            cart = self.system.get_user_cart(user_id) or {}

            items = tuple(sorted(
                (pid, qty) for pid, qty in cart.items() if qty > 0
            ))

            carts.add((user_id, items))

        orders = set()

        orders_data = self.system.get_orders()

        for oid, odata in orders_data.items():

            items = []
            total = 0

            for item in odata["items"]:
                name = item["name"]
                qty = item["quantity"]
                price = item["price"]

                items.append((name, qty))
                total += price * qty

            items_tuple = tuple(sorted(items))

            orders.add((
                oid,
                odata["status"],
                odata["user_id"],
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

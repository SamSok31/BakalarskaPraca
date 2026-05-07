from eshop_RooCode.output1_2 import EShopBackend, OrderStatus


class EShopSystem:

    def __init__(self):
        self.system = EShopBackend()


    def create_user(self, user_id: str):
        self.system.create_user(user_id)

    def delete_user(self, user_id: str):
        self.system.delete_user(user_id)


    def add_product(self, product_id: str, price: int, stock: int):
        self.system.add_product(product_id, product_id, price, stock)

    def delete_product(self, product_id: str):
        self.system.delete_product(product_id)


    def add_to_cart(self, user_id: str, product_id: str, quantity: int):
        self.system.add_to_cart(user_id, product_id, quantity)

    def remove_from_cart(self, user_id: str, product_id: str, quantity: int):
        self.system.remove_from_cart(user_id, product_id, quantity)


    def checkout(self, user_id: str):
        self.system.checkout(user_id)

    def update_order_status(self, order_id: str, new_status: str):
        status = OrderStatus[new_status.upper()]
        self.system.update_order_status(order_id, status)


    def get_state(self):
        users = set(self.system.users.keys())

        products = set()
        stock = set()

        for p in self.system.products.values():
            products.add((p.name, int(p.price)))
            stock.add((p.name, int(p.stock)))

        carts = set()

        for user_id in users:
            cart_items = self.system.carts.get(user_id, [])

            aggregated = {}

            for item in cart_items:
                if item.quantity > 0:
                    aggregated[item.name] = aggregated.get(item.name, 0) + item.quantity

            items_tuple = tuple(sorted(aggregated.items()))
            carts.add((user_id, items_tuple))

        orders = set()

        for order_id, order in self.system.orders.items():

            items = []
            total = 0

            for item in order.items:
                items.append((item.name, item.quantity))
                total += item.price * item.quantity

            items_tuple = tuple(sorted(items))

            status = order.status.name.lower()

            orders.add((
                order_id,
                status,
                order.user_id,
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

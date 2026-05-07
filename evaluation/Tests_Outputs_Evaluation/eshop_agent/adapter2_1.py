from eshop_agent.output2_1 import EShopSystem as GeneratedSystem


class EShopSystem:

    def __init__(self):
        self.system = GeneratedSystem()
        self.order_owner = {}


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
        order_id = self.system.checkout(user_id)
        if order_id:
            self.order_owner[order_id] = user_id
        return order_id


    def update_order_status(self, order_id: str, new_status: str):
        self.system.update_order_status(order_id, new_status)


    def get_state(self):
        state = self.system.get_system_state()

        users = set(state['users'].keys())


        products = set()
        stock = set()
        for p, data in state['products'].items():
            products.add((p, data['price']))
            stock.add((p, data['stock']))


        carts = set()
        for u, udata in state['users'].items():
            cart = udata.get('cart', {})
            items = tuple(sorted(cart.items()))
            carts.add((u, items))


        orders = set()
        for oid, odata in state['orders'].items():
            user_id = self.order_owner.get(oid, None)
            items = tuple(sorted(odata['items'].items()))
            total_price = int(odata['total_price'])

            orders.add((
                oid,
                odata['status'],
                user_id,
                items,
                total_price
            ))

        return {
            "users": users,
            "products": products,
            "stock": stock,
            "carts": carts,
            "orders": orders
        }

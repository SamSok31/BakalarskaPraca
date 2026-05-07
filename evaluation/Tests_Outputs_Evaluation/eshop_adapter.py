#TODO: Choose the correct generated code to import
from eshop_RooCode.output1_1 import EShopBackend as GeneratedSystem

class EShopSystem:

    def __init__(self):
        self.system = GeneratedSystem()


    def create_user(self, user_id: str):
        raise NotImplementedError

    def delete_user(self, user_id: str):
        raise NotImplementedError


    def add_product(self, product_id: str, price: int, stock: int):
        raise NotImplementedError

    def delete_product(self, product_id: str):
        raise NotImplementedError


    def add_to_cart(self, user_id: str, product_id: str, quantity: int):
        raise NotImplementedError

    def remove_from_cart(self, user_id: str, product_id: str, quantity: int):
        raise NotImplementedError
    

    def checkout(self, user_id: str):
        raise NotImplementedError

    def update_order_status(self, order_id: str, new_status: str):
        raise NotImplementedError


    def get_state(self):
        raise NotImplementedError

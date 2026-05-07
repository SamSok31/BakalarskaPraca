#TODO: Choose the correct adapter to connect the generated code with the tests
from eshop_RooCode.adapter1_1 import EShopSystem

from evaluation import evaluate_state


# A) USERS

def test_A1_create_user():
    system = EShopSystem()

    system.create_user("U1")

    expected = {
        "users": {"U1"},
        "products": set(),
        "stock": set(),
        "carts": {("U1", tuple())},
        "orders": set() }

    actual = system.get_state()
    evaluate_state(expected, actual)
    assert actual == expected


def test_A2_delete_user_without_carts_or_orders():
    system = EShopSystem()

    system.create_user("U1")
    system.delete_user("U1")

    expected = {
        "users": set(),
        "products": set(),
        "stock": set(),
        "carts": set(),
        "orders": set() }

    actual = system.get_state()
    evaluate_state(expected, actual)
    assert actual == expected


def test_A3_delete_user_with_cart():
    system = EShopSystem()

    system.create_user("U1")
    system.add_product("P1", price=10, stock=5)
    system.add_to_cart("U1", "P1", 2)
    system.delete_user("U1")

    expected = {
        "users": set(),
        "products": {("P1", 10)},
        "stock": {("P1", 5)},
        "carts": set(),
        "orders": set() }

    actual = system.get_state()
    evaluate_state(expected, actual)
    assert actual == expected


def test_A4_delete_user_with_order():
    system = EShopSystem()

    system.create_user("U1")
    system.add_product("P1", price=10, stock=5)
    system.add_to_cart("U1", "P1", 2)
    system.checkout("U1")
    system.delete_user("U1")

    expected = {
        "users": set(),
        "products": {("P1", 10)},
        "stock": {("P1", 3)},
        "carts": set(),
        "orders": {("SK00001", "pending", "U1", (("P1", 2),), 20)} }

    actual = system.get_state()
    evaluate_state(expected, actual)
    assert actual == expected


def test_A5_duplicate_user():
    system = EShopSystem()

    system.create_user("U1")
    system.create_user("U1")

    expected = {
        "users": {"U1"},
        "products": set(),
        "stock": set(),
        "carts": {("U1", tuple())},
        "orders": set() }

    actual = system.get_state()
    evaluate_state(expected, actual)
    assert actual == expected


def test_A6_delete_non_existing_user():
    system = EShopSystem()

    system.delete_user("U1")

    expected = {
        "users": set(),
        "products": set(),
        "stock": set(),
        "carts": set(),
        "orders": set() }

    actual = system.get_state()
    evaluate_state(expected, actual)
    assert actual == expected


def test_A7_delete_one_user_does_not_affect_others():
    system = EShopSystem()

    system.create_user("U1")
    system.create_user("U2")
    system.delete_user("U1")

    expected = {
        "users": {"U2"},
        "products": set(),
        "stock": set(),
        "carts": {("U2", tuple())},
        "orders": set() }

    actual = system.get_state()
    evaluate_state(expected, actual)
    assert actual == expected


def test_A8_create_multiple_users_and_carts():
    system = EShopSystem()

    system.create_user("U1")
    system.create_user("U2")
    system.create_user("U3")

    expected = {
        "users": {"U1", "U2", "U3"},
        "products": set(),
        "stock": set(),
        "carts": {
            ("U1", tuple()),
            ("U2", tuple()),
            ("U3", tuple()),
        },
        "orders": set()
    }

    actual = system.get_state()
    evaluate_state(expected, actual)
    assert actual == expected


def test_A9_delete_user_does_not_affect_other_user_cart():
    system = EShopSystem()

    system.create_user("U1")
    system.create_user("U2")

    system.add_product("P1", 10, 5)

    system.add_to_cart("U1", "P1", 2)
    system.add_to_cart("U2", "P1", 1)

    system.delete_user("U1")

    expected = {
        "users": {"U2"},
        "products": {("P1", 10)},
        "stock": {("P1", 4)},
        "carts": {
            ("U2", (("P1", 1),))
        },
        "orders": set()
    }

    actual = system.get_state()
    evaluate_state(expected, actual)
    assert actual == expected


def test_A10_delete_user_idempotent():
    system = EShopSystem()

    system.create_user("U1")
    system.delete_user("U1")
    system.delete_user("U1")

    expected = {
        "users": set(),
        "products": set(),
        "stock": set(),
        "carts": set(),
        "orders": set()
    }

    actual = system.get_state()
    evaluate_state(expected, actual)
    assert actual == expected


def test_A11_recreate_user_after_delete():
    system = EShopSystem()

    system.create_user("U1")
    system.delete_user("U1")
    system.create_user("U1")

    expected = {
        "users": {"U1"},
        "products": set(),
        "stock": set(),
        "carts": {("U1", tuple())},
        "orders": set()
    }

    actual = system.get_state()
    evaluate_state(expected, actual)
    assert actual == expected


def test_A12_multiple_orders_survive_user_delete():
    system = EShopSystem()

    system.create_user("U1")
    system.add_product("P1", 10, 10)

    system.add_to_cart("U1", "P1", 2)
    system.checkout("U1")

    system.add_to_cart("U1", "P1", 3)
    system.checkout("U1")

    system.delete_user("U1")

    expected = {
        "users": set(),
        "products": {("P1", 10)},
        "stock": {("P1", 5)},
        "carts": set(),
        "orders": {
            ("SK00001", "pending", "U1", (("P1", 2),), 20),
            ("SK00002", "pending", "U1", (("P1", 3),), 30),
        }
    }

    actual = system.get_state()
    evaluate_state(expected, actual)
    assert actual == expected



# B) PRODUCTS

def test_B1_create_product():
    system = EShopSystem()

    system.add_product("P1", price=10, stock=5)

    expected = {
        "users": set(),
        "products": {("P1", 10)},
        "stock": {("P1", 5)},
        "carts": set(),
        "orders": set() }

    actual = system.get_state()
    evaluate_state(expected, actual)
    assert actual == expected


def test_B2_duplicate_product():
    system = EShopSystem()

    system.add_product("P1", price=10, stock=5)
    system.add_product("P1", price=10, stock=5)

    expected = {
        "users": set(),
        "products": {("P1", 10)},
        "stock": {("P1", 10)},
        "carts": set(),
        "orders": set() }

    actual = system.get_state()
    evaluate_state(expected, actual)
    assert actual == expected


def test_B3_multiple_products():
    system = EShopSystem()

    system.add_product("P1", price=10, stock=5)
    system.add_product("P2", price=20, stock=3)

    expected = {
        "users": set(),
        "products": {("P1", 10), ("P2", 20)},
        "stock": {("P1", 5), ("P2", 3)},
        "carts": set(),
        "orders": set() }

    actual = system.get_state()
    evaluate_state(expected, actual)
    assert actual == expected


def test_B4_update_product_price():
    system = EShopSystem()

    system.add_product("P1", price=10, stock=5)
    system.add_product("P1", price=20, stock=5)

    expected = {
        "users": set(),
        "products": {("P1", 20)},
        "stock": {("P1", 10)},
        "carts": set(),
        "orders": set() }

    actual = system.get_state()
    evaluate_state(expected, actual)
    assert actual == expected


def test_B5_product_with_zero_stock():
    system = EShopSystem()

    system.add_product("P1", price=10, stock=0)

    expected = {
        "users": set(),
        "products": {("P1", 10)},
        "stock": {("P1", 0)},
        "carts": set(),
        "orders": set() }

    actual = system.get_state()
    evaluate_state(expected, actual)
    assert actual == expected


def test_B6_product_with_negative_stock():
    system = EShopSystem()

    system.add_product("P1", price=10, stock=-5)

    expected = {
        "users": set(),
        "products": set(),
        "stock": set(),
        "carts": set(),
        "orders": set() }

    actual = system.get_state()
    evaluate_state(expected, actual)
    assert actual == expected


def test_B7_multiple_product_updates():
    system = EShopSystem()

    system.add_product("P1", price=10, stock=5)
    system.add_product("P1", price=10, stock=3)
    system.add_product("P1", price=10, stock=2)

    expected = {
        "users": set(),
        "products": {("P1", 10)},
        "stock": {("P1", 10)},
        "carts": set(),
        "orders": set() }

    actual = system.get_state()
    evaluate_state(expected, actual)
    assert actual == expected


def test_B8_delete_product():
    system = EShopSystem()

    system.add_product("P1", price=10, stock=5)
    system.delete_product("P1")

    expected = {
        "users": set(),
        "products": set(),
        "stock": set(),
        "carts": set(),
        "orders": set()
    }

    actual = system.get_state()
    evaluate_state(expected, actual)
    assert actual == expected


def test_B9_delete_non_existing_product():
    system = EShopSystem()

    system.delete_product("P1")

    expected = {
        "users": set(),
        "products": set(),
        "stock": set(),
        "carts": set(),
        "orders": set()
    }

    actual = system.get_state()
    evaluate_state(expected, actual)
    assert actual == expected


def test_B10_delete_one_product_does_not_affect_others():
    system = EShopSystem()

    system.add_product("P1", price=10, stock=5)
    system.add_product("P2", price=20, stock=3)

    system.delete_product("P1")

    expected = {
        "users": set(),
        "products": {("P2", 20)},
        "stock": {("P2", 3)},
        "carts": set(),
        "orders": set()
    }

    actual = system.get_state()
    evaluate_state(expected, actual)
    assert actual == expected


def test_B11_delete_product_does_not_affect_carts():
    system = EShopSystem()

    system.create_user("U1")
    system.add_product("P1", price=10, stock=5)

    system.add_to_cart("U1", "P1", 2)
    system.delete_product("P1")

    expected = {
        "users": {"U1"},
        "products": set(),
        "stock": set(),
        "carts": {("U1", (("P1", 2),))},
        "orders": set()
    }

    actual = system.get_state()
    evaluate_state(expected, actual)
    assert actual == expected


def test_B12_delete_product_after_order():
    system = EShopSystem()

    system.create_user("U1")
    system.add_product("P1", price=10, stock=5)

    system.add_to_cart("U1", "P1", 2)
    system.checkout("U1")

    system.delete_product("P1")

    expected = {
        "users": {"U1"},
        "products": set(),
        "stock": set(),
        "carts": {("U1", tuple())},
        "orders": {("SK00001", "pending", "U1", (("P1", 2),), 20)}
    }

    actual = system.get_state()
    evaluate_state(expected, actual)
    assert actual == expected


def test_B13_recreate_product_after_delete():
    system = EShopSystem()

    system.add_product("P1", price=10, stock=5)
    system.delete_product("P1")
    system.add_product("P1", price=20, stock=3)

    expected = {
        "users": set(),
        "products": {("P1", 20)},
        "stock": {("P1", 3)},
        "carts": set(),
        "orders": set()
    }

    actual = system.get_state()
    evaluate_state(expected, actual)
    assert actual == expected


def test_B14_update_product_with_existing_cart():
    system = EShopSystem()

    system.create_user("U1")
    system.add_product("P1", price=10, stock=5)

    system.add_to_cart("U1", "P1", 2)
    system.add_product("P1", price=20, stock=3)

    expected = {
        "users": {"U1"},
        "products": {("P1", 20)},
        "stock": {("P1", 6)},
        "carts": {("U1", (("P1", 2),))},
        "orders": set()
    }

    actual = system.get_state()
    evaluate_state(expected, actual)
    assert actual == expected


def test_B15_add_to_cart_after_product_deleted():
    system = EShopSystem()

    system.create_user("U1")
    system.add_product("P1", 10, 5)

    system.delete_product("P1")
    system.add_to_cart("U1", "P1", 1)

    expected = {
        "users": {"U1"},
        "products": set(),
        "stock": set(),
        "carts": {("U1", tuple())},
        "orders": set()
    }

    actual = system.get_state()
    evaluate_state(expected, actual)
    assert actual == expected


def test_B16_multiple_updates_with_price_changes():
    system = EShopSystem()

    system.add_product("P1", price=10, stock=5)
    system.add_product("P1", price=20, stock=3)
    system.add_product("P1", price=15, stock=2)

    expected = {
        "users": set(),
        "products": {("P1", 15)},
        "stock": {("P1", 10)},
        "carts": set(),
        "orders": set()
    }

    actual = system.get_state()
    evaluate_state(expected, actual)
    assert actual == expected



# C) CART OPERATIONS

def test_C1_add_to_cart():
    system = EShopSystem()

    system.create_user("U1")
    system.add_product("P1", price=10, stock=5)
    system.add_to_cart("U1", "P1", 2)

    expected = {
        "users": {"U1"},
        "products": {("P1", 10)},
        "stock": {("P1", 3)},
        "carts": {("U1", (("P1", 2),))},
        "orders": set() }

    actual = system.get_state()
    evaluate_state(expected, actual)
    assert actual == expected


def test_C2_remove_from_cart():
    system = EShopSystem()

    system.create_user("U1")
    system.add_product("P1", price=10, stock=5)
    system.add_to_cart("U1", "P1", 2)
    system.remove_from_cart("U1", "P1", 2)

    expected = {
        "users": {"U1"},
        "products": {("P1", 10)},
        "stock": {("P1", 5)},
        "carts": {("U1", tuple())},
        "orders": set() }

    actual = system.get_state()
    evaluate_state(expected, actual)
    assert actual == expected


def test_C3_add_more_than_stock():
    system = EShopSystem()

    system.create_user("U1")
    system.add_product("P1", price=10, stock=5)
    system.add_to_cart("U1", "P1", 10)

    expected = {
        "users": {"U1"},
        "products": {("P1", 10)},
        "stock": {("P1", 5)},
        "carts": {("U1", tuple())},
        "orders": set() }

    actual = system.get_state()
    evaluate_state(expected, actual)
    assert actual == expected


def test_C4_add_multiple_products():
    system = EShopSystem()

    system.create_user("U1")
    system.add_product("P1", price=10, stock=5)
    system.add_product("P2", price=20, stock=3)

    system.add_to_cart("U1", "P1", 2)
    system.add_to_cart("U1", "P2", 1)

    expected = {
        "users": {"U1"},
        "products": {("P1", 10), ("P2", 20)},
        "stock": {("P1", 3), ("P2", 2)},
        "carts": {("U1", (("P1", 2), ("P2", 1)))},
        "orders": set() }

    actual = system.get_state()
    evaluate_state(expected, actual)
    assert actual == expected


def test_C5_remove_non_existing_item():
    system = EShopSystem()

    system.create_user("U1")
    system.add_product("P1", price=10, stock=5)
    system.remove_from_cart("U1", "P1", 1)

    expected = {
        "users": {"U1"},
        "products": {("P1", 10)},
        "stock": {("P1", 5)},
        "carts": {("U1", tuple())},
        "orders": set() }

    actual = system.get_state()
    evaluate_state(expected, actual)
    assert actual == expected


def test_C6_add_same_product_multiple_times():
    system = EShopSystem()

    system.create_user("U1")
    system.add_product("P1", price=10, stock=5)

    system.add_to_cart("U1", "P1", 2)
    system.add_to_cart("U1", "P1", 1)

    expected = {
        "users": {"U1"},
        "products": {("P1", 10)},
        "stock": {("P1", 2)},
        "carts": {("U1", (("P1", 3),))},
        "orders": set() }

    actual = system.get_state()
    evaluate_state(expected, actual)
    assert actual == expected


def test_C7_negative_quantity():
    system = EShopSystem()

    system.create_user("U1")
    system.add_product("P1", price=10, stock=5)
    system.add_to_cart("U1", "P1", -1)

    expected = {
        "users": {"U1"},
        "products": {("P1", 10)},
        "stock": {("P1", 5)},
        "carts": {("U1", tuple())},
        "orders": set() }

    actual = system.get_state()
    evaluate_state(expected, actual)
    assert actual == expected


def test_C8_zero_quantity():
    system = EShopSystem()

    system.create_user("U1")
    system.add_product("P1", price=10, stock=5)
    system.add_to_cart("U1", "P1", 0)

    expected = {
        "users": {"U1"},
        "products": {("P1", 10)},
        "stock": {("P1", 5)},
        "carts": {("U1", tuple())},
        "orders": set() }

    actual = system.get_state()
    evaluate_state(expected, actual)
    assert actual == expected


def test_C9_add_after_stock_depleted():
    system = EShopSystem()

    system.create_user("U1")
    system.add_product("P1", price=10, stock=1)

    system.add_to_cart("U1", "P1", 1)
    system.checkout("U1")
    system.add_to_cart("U1", "P1", 1)

    expected = {
        "users": {"U1"},
        "products": {("P1", 10)},
        "stock": {("P1", 0)},
        "carts": {("U1", tuple())},
        "orders": {("SK00001", "pending", "U1", (("P1", 1),), 10)} }

    actual = system.get_state()

    evaluate_state(expected, actual)
    assert actual == expected


def test_C10_carts_independence():
    system = EShopSystem()

    system.create_user("U1")
    system.create_user("U2")
    system.add_product("P1", price=10, stock=5)

    system.add_to_cart("U1", "P1", 2)
    system.add_to_cart("U2", "P1", 1)

    expected = {
        "users": {"U1", "U2"},
        "products": {("P1", 10)},
        "stock": {("P1", 2)},
        "carts": {
            ("U1", (("P1", 2),)),
            ("U2", (("P1", 1),)),
        },
        "orders": set() }

    actual = system.get_state()

    evaluate_state(expected, actual)
    assert actual == expected


def test_C11_reservation_blocks_other_users():
    system = EShopSystem()

    system.create_user("U1")
    system.create_user("U2")
    system.add_product("P1", 10, 5)

    system.add_to_cart("U1", "P1", 5)
    system.add_to_cart("U2", "P1", 1)

    expected = {
        "users": {"U1", "U2"},
        "products": {("P1", 10)},
        "stock": {("P1", 0)},
        "carts": {
            ("U1", (("P1", 5),)),
            ("U2", tuple()),
        },
        "orders": set()
    }

    actual = system.get_state()
    evaluate_state(expected, actual)
    assert actual == expected


def test_C12_remove_restores_stock():
    system = EShopSystem()

    system.create_user("U1")
    system.add_product("P1", 10, 5)

    system.add_to_cart("U1", "P1", 3)
    system.remove_from_cart("U1", "P1", 3)

    expected = {
        "users": {"U1"},
        "products": {("P1", 10)},
        "stock": {("P1", 5)},
        "carts": {("U1", tuple())},
        "orders": set()
    }

    actual = system.get_state()
    evaluate_state(expected, actual)
    assert actual == expected


def test_C13_interleaved_reservations():
    system = EShopSystem()

    system.create_user("U1")
    system.create_user("U2")
    system.add_product("P1", 10, 3)

    system.add_to_cart("U1", "P1", 2)
    system.add_to_cart("U2", "P1", 2) 

    expected = {
        "users": {"U1", "U2"},
        "products": {("P1", 10)},
        "stock": {("P1", 1)},
        "carts": {
            ("U1", (("P1", 2),)),
            ("U2", tuple()),
        },
        "orders": set()
    }

    actual = system.get_state()
    evaluate_state(expected, actual)
    assert actual == expected


def test_C14_partial_remove_from_cart():
    system = EShopSystem()

    system.create_user("U1")
    system.add_product("P1", 10, 5)

    system.add_to_cart("U1", "P1", 4)
    system.remove_from_cart("U1", "P1", 2)

    expected = {
        "users": {"U1"},
        "products": {("P1", 10)},
        "stock": {("P1", 3)},
        "carts": {("U1", (("P1", 2),))},
        "orders": set()
    }

    actual = system.get_state()
    evaluate_state(expected, actual)
    assert actual == expected


def test_C15_remove_more_than_exists():
    system = EShopSystem()

    system.create_user("U1")
    system.add_product("P1", 10, 5)

    system.add_to_cart("U1", "P1", 2)
    system.remove_from_cart("U1", "P1", 5)

    expected = {
        "users": {"U1"},
        "products": {("P1", 10)},
        "stock": {("P1", 3)},
        "carts": {("U1", (("P1", 2),))},
        "orders": set()
    }

    actual = system.get_state()
    evaluate_state(expected, actual)
    assert actual == expected


def test_C16_remove_zero_quantity():
    system = EShopSystem()

    system.create_user("U1")
    system.add_product("P1", 10, 5)

    system.add_to_cart("U1", "P1", 2)
    system.remove_from_cart("U1", "P1", 0)

    expected = {
        "users": {"U1"},
        "products": {("P1", 10)},
        "stock": {("P1", 3)},
        "carts": {("U1", (("P1", 2),))},
        "orders": set()
    }

    actual = system.get_state()
    evaluate_state(expected, actual)
    assert actual == expected


def test_C17_remove_negative_quantity():
    system = EShopSystem()

    system.create_user("U1")
    system.add_product("P1", 10, 5)

    system.add_to_cart("U1", "P1", 2)
    system.remove_from_cart("U1", "P1", -1)

    expected = {
        "users": {"U1"},
        "products": {("P1", 10)},
        "stock": {("P1", 3)},
        "carts": {("U1", (("P1", 2),))},
        "orders": set()
    }

    actual = system.get_state()
    evaluate_state(expected, actual)
    assert actual == expected


def test_C18_remove_frees_stock_for_other_users():
    system = EShopSystem()

    system.create_user("U1")
    system.create_user("U2")
    system.add_product("P1", 10, 3)

    system.add_to_cart("U1", "P1", 3)
    system.remove_from_cart("U1", "P1", 2)

    system.add_to_cart("U2", "P1", 2)

    expected = {
        "users": {"U1", "U2"},
        "products": {("P1", 10)},
        "stock": {("P1", 0)},
        "carts": {
            ("U1", (("P1", 1),)),
            ("U2", (("P1", 2),)),
        },
        "orders": set()
    }

    actual = system.get_state()
    evaluate_state(expected, actual)
    assert actual == expected



# D) CHECKOUT

def test_D1_successful_checkout():
    system = EShopSystem()

    system.create_user("U1")
    system.add_product("P1", price=10, stock=5)
    system.add_to_cart("U1", "P1", 2)
    system.checkout("U1")

    expected = {
        "users": {"U1"},
        "products": {("P1", 10)},
        "stock": {("P1", 3)},
        "carts": {("U1", tuple())},
        "orders": {("SK00001", "pending", "U1", (("P1", 2),), 20)} }

    actual = system.get_state()
    evaluate_state(expected, actual)
    assert actual == expected


def test_D2_checkout_empty_cart():
    system = EShopSystem()

    system.create_user("U1")
    system.checkout("U1")

    expected = {
        "users": {"U1"},
        "products": set(),
        "stock": set(),
        "carts": {("U1", tuple())},
        "orders": set() }

    actual = system.get_state()
    evaluate_state(expected, actual)
    assert actual == expected


def test_D3_checkout_insufficient_stock():
    system = EShopSystem()

    system.create_user("U1")
    system.create_user("U2")
    system.add_product("P1", price=10, stock=2)

    system.add_to_cart("U1", "P1", 2)
    system.add_to_cart("U2", "P1", 2)

    system.checkout("U1")
    system.checkout("U2")

    expected = {
        "users": {"U1", "U2"},
        "products": {("P1", 10)},
        "stock": {("P1", 0)},
        "carts": {
            ("U1", tuple()),
            ("U2", tuple()),
        },
        "orders": {("SK00001", "pending", "U1", (("P1", 2),), 20)} }

    actual = system.get_state()
    evaluate_state(expected, actual)
    assert actual == expected


def test_D4_checkout_multiple_products():
    system = EShopSystem()

    system.create_user("U1")
    system.add_product("P1", price=10, stock=5)
    system.add_product("P2", price=20, stock=3)

    system.add_to_cart("U1", "P1", 2)
    system.add_to_cart("U1", "P2", 1)

    system.checkout("U1")

    expected = {
        "users": {"U1"},
        "products": {("P1", 10), ("P2", 20)},
        "stock": {("P1", 3), ("P2", 2)},
        "carts": {("U1", tuple())},
        "orders": {("SK00001", "pending", "U1", (("P1", 2), ("P2", 1)), 40)} }

    actual = system.get_state()
    evaluate_state(expected, actual)
    assert actual == expected


def test_D5_partial_availability_failure():
    system = EShopSystem()

    system.create_user("U1")

    system.add_product("P1", price=10, stock=2)
    system.add_product("P2", price=20, stock=0)

    system.add_to_cart("U1", "P1", 2)
    system.add_to_cart("U1", "P2", 1)

    system.checkout("U1")

    expected = {
        "users": {"U1"},
        "products": {("P1", 10), ("P2", 20)},
        "stock": {("P1", 0), ("P2", 0)},
        "carts": {("U1", tuple())},
        "orders": {("SK00001", "pending", "U1", (("P1", 2),), 20)} }

    actual = system.get_state()
    evaluate_state(expected, actual)
    assert actual == expected


def test_D6_checkout_after_cart_update():
    system = EShopSystem()

    system.create_user("U1")
    system.add_product("P1", price=10, stock=5)

    system.add_to_cart("U1", "P1", 3)
    system.remove_from_cart("U1", "P1", 3)
    system.add_to_cart("U1", "P1", 2)

    system.checkout("U1")

    expected = {
        "users": {"U1"},
        "products": {("P1", 10)},
        "stock": {("P1", 3)},
        "carts": {("U1", tuple())},
        "orders": {("SK00001", "pending", "U1", (("P1", 2),), 20)} }

    actual = system.get_state()
    evaluate_state(expected, actual)
    assert actual == expected


def test_D7_double_checkout():
    system = EShopSystem()

    system.create_user("U1")
    system.add_product("P1", 10, 5)

    system.add_to_cart("U1", "P1", 2)
    system.checkout("U1")
    system.checkout("U1")

    expected = {
        "users": {"U1"},
        "products": {("P1", 10)},
        "stock": {("P1", 3)},
        "carts": {("U1", tuple())},
        "orders": {
            ("SK00001", "pending", "U1", (("P1", 2),), 20)
        }
    }

    actual = system.get_state()
    evaluate_state(expected, actual)
    assert actual == expected


def test_D8_checkout_non_existing_user():
    system = EShopSystem()

    system.checkout("U1")

    expected = {
        "users": set(),
        "products": set(),
        "stock": set(),
        "carts": set(),
        "orders": set()
    }

    actual = system.get_state()
    evaluate_state(expected, actual)
    assert actual == expected


def test_D9_stock_consistency_after_checkout():
    system = EShopSystem()

    system.create_user("U1")
    system.create_user("U2")

    system.add_product("P1", 10, 5)

    system.add_to_cart("U1", "P1", 3)
    system.add_to_cart("U2", "P1", 2)

    system.checkout("U1")

    expected = {
        "users": {"U1", "U2"},
        "products": {("P1", 10)},
        "stock": {("P1", 0)},
        "carts": {
            ("U1", tuple()),
            ("U2", (("P1", 2),)),
        },
        "orders": {
            ("SK00001", "pending", "U1", (("P1", 3),), 30)
        }
    }

    actual = system.get_state()
    evaluate_state(expected, actual)
    assert actual == expected


# E) ORDERS

def test_E1_update_order_status():
    system = EShopSystem()

    system.create_user("U1")
    system.add_product("P1", 10, 5)

    system.add_to_cart("U1", "P1", 2)
    system.checkout("U1")

    

    system.update_order_status("SK00001", "processing")


    expected = {
        "users": {"U1"},
        "products": {("P1", 10)},
        "stock": {("P1", 3)},
        "carts": {("U1", tuple())},
        "orders": {("SK00001", "processing", "U1", (("P1", 2),), 20)}
    }

    actual = system.get_state()
    evaluate_state(expected, actual)
    assert actual == expected


def test_E2_cancel_order_restores_stock():
    system = EShopSystem()

    system.create_user("U1")
    system.add_product("P1", 10, 5)

    system.add_to_cart("U1", "P1", 2)
    system.checkout("U1")

    system.update_order_status("SK00001", "cancelled")

    expected = {
        "users": {"U1"},
        "products": {("P1", 10)},
        "stock": {("P1", 5)},
        "carts": {("U1", tuple())},
        "orders": {("SK00001", "cancelled", "U1", (("P1", 2),), 20)}
    }

    actual = system.get_state()
    evaluate_state(expected, actual)
    assert actual == expected


def test_E3_cancel_recreates_deleted_product():
    system = EShopSystem()

    system.create_user("U1")
    system.add_product("P1", 10, 5)

    system.add_to_cart("U1", "P1", 2)
    system.checkout("U1")

    system.delete_product("P1")
    system.update_order_status("SK00001", "cancelled")

    expected = {
        "users": {"U1"},
        "products": {("P1", 10)},
        "stock": {("P1", 2)},
        "carts": {("U1", tuple())},
        "orders": {("SK00001", "cancelled", "U1", (("P1", 2),), 20)}
    }

    actual = system.get_state()
    evaluate_state(expected, actual)
    assert actual == expected


def test_E4_cancel_idempotent():
    system = EShopSystem()

    system.create_user("U1")
    system.add_product("P1", 10, 5)

    system.add_to_cart("U1", "P1", 2)
    system.checkout("U1")

    system.update_order_status("SK00001", "cancelled")
    system.update_order_status("SK00001", "cancelled")

    expected = {
        "users": {"U1"},
        "products": {("P1", 10)},
        "stock": {("P1", 5)},
        "carts": {("U1", tuple())},
        "orders": {("SK00001", "cancelled", "U1", (("P1", 2),), 20)}
    }

    actual = system.get_state()
    evaluate_state(expected, actual)
    assert actual == expected


def test_E5_update_non_existing_order():
    system = EShopSystem()

    system.update_order_status("SK00001", "cancelled")

    expected = {
        "users": set(),
        "products": set(),
        "stock": set(),
        "carts": set(),
        "orders": set()
    }

    actual = system.get_state()
    evaluate_state(expected, actual)
    assert actual == expected


def test_E6_multiple_orders_cancel_independent():
    system = EShopSystem()

    system.create_user("U1")
    system.add_product("P1", 10, 10)

    system.add_to_cart("U1", "P1", 2)
    system.checkout("U1")

    system.add_to_cart("U1", "P1", 3)
    system.checkout("U1")

    system.update_order_status("SK00001", "cancelled")

    expected = {
        "users": {"U1"},
        "products": {("P1", 10)},
        "stock": {("P1", 7)},
        "carts": {("U1", tuple())},
        "orders": {
            ("SK00001", "cancelled", "U1", (("P1", 2),), 20),
            ("SK00002", "pending", "U1", (("P1", 3),), 30),
        }
    }

    actual = system.get_state()
    evaluate_state(expected, actual)
    assert actual == expected


def test_E7_order_id_sequence():
    system = EShopSystem()

    system.create_user("U1")
    system.add_product("P1", 10, 10)

    system.add_to_cart("U1", "P1", 1)
    system.checkout("U1")

    system.add_to_cart("U1", "P1", 1)
    system.checkout("U1")

    system.add_to_cart("U1", "P1", 1)
    system.checkout("U1")

    expected = {
        "users": {"U1"},
        "products": {("P1", 10)},
        "stock": {("P1", 7)},
        "carts": {("U1", tuple())},
        "orders": {
            ("SK00001", "pending", "U1", (("P1", 1),), 10),
            ("SK00002", "pending", "U1", (("P1", 1),), 10),
            ("SK00003", "pending", "U1", (("P1", 1),), 10),
        }
    }

    actual = system.get_state()
    evaluate_state(expected, actual)
    assert actual == expected


def test_E8_invalid_status_ignored():
    system = EShopSystem()

    system.create_user("U1")
    system.add_product("P1", 10, 5)

    system.add_to_cart("U1", "P1", 2)
    system.checkout("U1")

    system.update_order_status("SK00001", "INVALID")

    expected = {
        "users": {"U1"},
        "products": {("P1", 10)},
        "stock": {("P1", 3)},
        "carts": {("U1", tuple())},
        "orders": {("SK00001", "pending", "U1", (("P1", 2),), 20)}
    }

    actual = system.get_state()
    evaluate_state(expected, actual)
    assert actual == expected


def test_E9_cancel_does_not_duplicate_stock():
    system = EShopSystem()

    system.create_user("U1")
    system.add_product("P1", 10, 5)

    system.add_to_cart("U1", "P1", 2)
    system.checkout("U1")

    system.update_order_status("SK00001", "cancelled")
    system.update_order_status("SK00001", "processing")
    system.update_order_status("SK00001", "cancelled")

    expected = {
        "users": {"U1"},
        "products": {("P1", 10)},
        "stock": {("P1", 5)},
        "carts": {("U1", tuple())},
        "orders": {("SK00001", "cancelled", "U1", (("P1", 2),), 20)}
    }

    actual = system.get_state()
    evaluate_state(expected, actual)
    assert actual == expected


def test_E10_price_changes_before_checkout():
    system = EShopSystem()

    system.create_user("U1")
    system.add_product("P1", 10, 5)

    system.add_to_cart("U1", "P1", 2)

    system.add_product("P1", 20, 0)

    system.checkout("U1")

    expected = {
        "users": {"U1"},
        "products": {("P1", 20)},
        "stock": {("P1", 3)},
        "carts": {("U1", tuple())},
        "orders": {("SK00001", "pending", "U1", (("P1", 2),), 40)}
    }

    actual = system.get_state()
    evaluate_state(expected, actual)
    assert actual == expected


def test_E11_valid_status_progression():
    system = EShopSystem()

    system.create_user("U1")
    system.add_product("P1", 10, 5)

    system.add_to_cart("U1", "P1", 1)
    system.checkout("U1")

    system.update_order_status("SK00001", "processing")
    system.update_order_status("SK00001", "completed")
    system.update_order_status("SK00001", "shipped")
    system.update_order_status("SK00001", "delivered")

    expected = {
        "users": {"U1"},
        "products": {("P1", 10)},
        "stock": {("P1", 4)},
        "carts": {("U1", tuple())},
        "orders": {
            ("SK00001", "delivered", "U1", (("P1", 1),), 10)
        }
    }

    actual = system.get_state()
    evaluate_state(expected, actual)
    assert actual == expected


def test_E12_invalid_skip_transition():
    system = EShopSystem()

    system.create_user("U1")
    system.add_product("P1", 10, 5)

    system.add_to_cart("U1", "P1", 1)
    system.checkout("U1")

    system.update_order_status("SK00001", "shipped")

    expected = {
        "users": {"U1"},
        "products": {("P1", 10)},
        "stock": {("P1", 4)},
        "carts": {("U1", tuple())},
        "orders": {
            ("SK00001", "pending", "U1", (("P1", 1),), 10)
        }
    }

    actual = system.get_state()
    evaluate_state(expected, actual)
    assert actual == expected


def test_E13_invalid_backward_transition():
    system = EShopSystem()

    system.create_user("U1")
    system.add_product("P1", 10, 5)

    system.add_to_cart("U1", "P1", 1)
    system.checkout("U1")

    system.update_order_status("SK00001", "processing")
    system.update_order_status("SK00001", "pending")

    expected = {
        "users": {"U1"},
        "products": {("P1", 10)},
        "stock": {("P1", 4)},
        "carts": {("U1", tuple())},
        "orders": {
            ("SK00001", "processing", "U1", (("P1", 1),), 10)
        }
    }

    actual = system.get_state()
    evaluate_state(expected, actual)
    assert actual == expected


def test_E14_no_transition_after_delivered():
    system = EShopSystem()

    system.create_user("U1")
    system.add_product("P1", 10, 5)

    system.add_to_cart("U1", "P1", 1)
    system.checkout("U1")

    system.update_order_status("SK00001", "processing")
    system.update_order_status("SK00001", "completed")
    system.update_order_status("SK00001", "shipped")
    system.update_order_status("SK00001", "delivered")

    system.update_order_status("SK00001", "processing")

    expected = {
        "users": {"U1"},
        "products": {("P1", 10)},
        "stock": {("P1", 4)},
        "carts": {("U1", tuple())},
        "orders": {
            ("SK00001", "delivered", "U1", (("P1", 1),), 10)
        }
    }

    actual = system.get_state()
    evaluate_state(expected, actual)
    assert actual == expected


def test_E15_cancel_transition_after_delivered():
    system = EShopSystem()

    system.create_user("U1")
    system.add_product("P1", 10, 5)

    system.add_to_cart("U1", "P1", 1)
    system.checkout("U1")

    system.update_order_status("SK00001", "processing")
    system.update_order_status("SK00001", "completed")
    system.update_order_status("SK00001", "shipped")
    system.update_order_status("SK00001", "delivered")

    system.update_order_status("SK00001", "cancelled")

    expected = {
        "users": {"U1"},
        "products": {("P1", 10)},
        "stock": {("P1", 5)},
        "carts": {("U1", tuple())},
        "orders": {
            ("SK00001", "cancelled", "U1", (("P1", 1),), 10)
        }
    }

    actual = system.get_state()
    evaluate_state(expected, actual)
    assert actual == expected


def test_E16_cancel_from_processing():
    system = EShopSystem()

    system.create_user("U1")
    system.add_product("P1", 10, 5)

    system.add_to_cart("U1", "P1", 2)
    system.checkout("U1")

    system.update_order_status("SK00001", "processing")
    system.update_order_status("SK00001", "cancelled")

    expected = {
        "users": {"U1"},
        "products": {("P1", 10)},
        "stock": {("P1", 5)},
        "carts": {("U1", tuple())},
        "orders": {
            ("SK00001", "cancelled", "U1", (("P1", 2),), 20)
        }
    }

    actual = system.get_state()
    evaluate_state(expected, actual)
    assert actual == expected


def test_E17_multiple_orders_cancel_independent():
    system = EShopSystem()

    system.create_user("U1")
    system.add_product("P1", 10, 10)

    system.add_to_cart("U1", "P1", 2)
    system.checkout("U1")

    system.update_order_status("SK00001", "cancelled")

    system.add_to_cart("U1", "P1", 3)
    system.checkout("U1")

    expected = {
        "users": {"U1"},
        "products": {("P1", 10)},
        "stock": {("P1", 7)},
        "carts": {("U1", tuple())},
        "orders": {
            ("SK00001", "cancelled", "U1", (("P1", 2),), 20),
            ("SK00002", "pending", "U1", (("P1", 3),), 30),
        }
    }

    actual = system.get_state()
    evaluate_state(expected, actual)
    assert actual == expected



# F) COMPLEX SCENÁRE

def test_F1_loop_add_to_cart():
    system = EShopSystem()

    system.create_user("U1")
    system.add_product("P1", price=10, stock=5)

    for _ in [1, 2, 3]:
        system.add_to_cart("U1", "P1", 1)

    expected = {
        "users": {"U1"},
        "products": {("P1", 10)},
        "stock": {("P1", 2)},
        "carts": {("U1", (("P1", 3),))},
        "orders": set() }

    actual = system.get_state()
    evaluate_state(expected, actual)
    assert actual == expected


def test_F2_multiple_users_checkout():
    system = EShopSystem()

    system.create_user("U1")
    system.create_user("U2")
    system.add_product("P1", price=10, stock=5)

    system.add_to_cart("U1", "P1", 2)
    system.add_to_cart("U2", "P1", 2)

    system.checkout("U1")
    system.checkout("U2")

    expected = {
        "users": {"U1", "U2"},
        "products": {("P1", 10)},
        "stock": {("P1", 1)},
        "carts": {
            ("U1", tuple()),
            ("U2", tuple()) },
        "orders": {
            ("SK00001", "pending", "U1", (("P1", 2),), 20),
            ("SK00002", "pending", "U2", (("P1", 2),), 20) } }

    actual = system.get_state()
    evaluate_state(expected, actual)
    assert actual == expected


def test_F3_mixed_operations():
    system = EShopSystem()

    system.create_user("U1")
    system.add_product("P1", price=10, stock=5)

    system.add_to_cart("U1", "P1", 2)
    system.remove_from_cart("U1", "P1", 2)
    system.add_to_cart("U1", "P1", 3)

    system.checkout("U1")

    expected = {
        "users": {"U1"},
        "products": {("P1", 10)},
        "stock": {("P1", 2)},
        "carts": {("U1", tuple())},
        "orders": {("SK00001", "pending", "U1", (("P1", 3),), 30)} }

    actual = system.get_state()
    evaluate_state(expected, actual)
    assert actual == expected


def test_F4_interleaved_operations_with_stock_conflict():
    system = EShopSystem()

    system.create_user("U1")
    system.create_user("U2")
    system.add_product("P1", price=10, stock=3)

    system.add_to_cart("U1", "P1", 2)
    system.add_to_cart("U2", "P1", 2)

    system.checkout("U1")
    system.add_to_cart("U2", "P1", 1)
    system.checkout("U2")

    expected = {
        "users": {"U1", "U2"},
        "products": {("P1", 10)},
        "stock": {("P1", 0)},
        "carts": {
            ("U1", tuple()),
            ("U2", tuple()) },
        "orders": {("SK00001", "pending", "U1", (("P1", 2),), 20),
                   ("SK00002", "pending", "U2", (("P1", 1),), 10)} }

    actual = system.get_state()
    evaluate_state(expected, actual)
    assert actual == expected


def test_F5_full_system_flow():
    system = EShopSystem()

    system.create_user("U1")
    system.create_user("U2")

    system.add_product("P1", price=10, stock=5)
    system.add_product("P2", price=20, stock=3)

    system.add_to_cart("U1", "P1", 2)
    system.add_to_cart("U1", "P2", 1)

    system.add_to_cart("U2", "P1", 3)

    system.checkout("U1")
    system.checkout("U2")

    expected = {
        "users": {"U1", "U2"},
        "products": {("P1", 10), ("P2", 20)},
        "stock": {("P1", 0), ("P2", 2)},
        "carts": {
            ("U1", tuple()),
            ("U2", tuple()) },
        "orders": {
            ("SK00001", "pending", "U1", (("P1", 2), ("P2", 1)), 40),
            ("SK00002", "pending", "U2", (("P1", 3),), 30) } }

    actual = system.get_state()
    evaluate_state(expected, actual)
    assert actual == expected


def test_F6_cancel_then_reuse_stock():
    system = EShopSystem()

    system.create_user("U1")
    system.create_user("U2")

    system.add_product("P1", 10, 5)

    system.add_to_cart("U1", "P1", 5)
    system.checkout("U1")

    system.update_order_status("SK00001", "cancelled")

    system.add_to_cart("U2", "P1", 5)
    system.checkout("U2")

    expected = {
        "users": {"U1", "U2"},
        "products": {("P1", 10)},
        "stock": {("P1", 0)},
        "carts": {
            ("U1", tuple()),
            ("U2", tuple()),
        },
        "orders": {
            ("SK00001", "cancelled", "U1", (("P1", 5),), 50),
            ("SK00002", "pending", "U2", (("P1", 5),), 50),
        }
    }

    actual = system.get_state()
    evaluate_state(expected, actual)
    assert actual == expected


def test_F7_delete_then_cancel_then_reuse():
    system = EShopSystem()

    system.create_user("U1")
    system.create_user("U2")

    system.add_product("P1", 10, 5)

    system.add_to_cart("U1", "P1", 3)
    system.checkout("U1")

    system.delete_product("P1")

    system.update_order_status("SK00001", "cancelled")

    system.add_to_cart("U2", "P1", 3)

    expected = {
        "users": {"U1", "U2"},
        "products": {("P1", 10)},
        "stock": {("P1", 0)},
        "carts": {
            ("U1", tuple()),
            ("U2", (("P1", 3),)),
        },
        "orders": {
            ("SK00001", "cancelled", "U1", (("P1", 3),), 30),
        }
    }

    actual = system.get_state()
    evaluate_state(expected, actual)
    assert actual == expected


def test_F8_price_change_with_reservations():
    system = EShopSystem()

    system.create_user("U1")
    system.create_user("U2")

    system.add_product("P1", 10, 5)

    system.add_to_cart("U1", "P1", 2)

    system.add_product("P1", 20, 0)

    system.add_to_cart("U2", "P1", 3)

    system.checkout("U1")
    system.checkout("U2")

    expected = {
        "users": {"U1", "U2"},
        "products": {("P1", 20)},
        "stock": {("P1", 0)},
        "carts": {
            ("U1", tuple()),
            ("U2", tuple()),
        },
        "orders": {
            ("SK00001", "pending", "U1", (("P1", 2),), 40),
            ("SK00002", "pending", "U2", (("P1", 3),), 60),
        }
    }

    actual = system.get_state()
    evaluate_state(expected, actual)
    assert actual == expected


def test_F9_long_mixed_sequence():
    system = EShopSystem()

    system.create_user("U1")
    system.create_user("U2")

    system.add_product("P1", 10, 10)

    system.add_to_cart("U1", "P1", 3)
    system.add_to_cart("U2", "P1", 4)

    system.remove_from_cart("U2", "P1", 2)

    system.checkout("U1")

    system.update_order_status("SK00001", "processing")

    system.add_to_cart("U2", "P1", 3)

    system.update_order_status("SK00001", "cancelled")

    system.checkout("U2")

    expected = {
        "users": {"U1", "U2"},
        "products": {("P1", 10)},
        "stock": {("P1", 5)},
        "carts": {
            ("U1", tuple()),
            ("U2", tuple()),
        },
        "orders": {
            ("SK00001", "cancelled", "U1", (("P1", 3),), 30),
            ("SK00002", "pending", "U2", (("P1", 5),), 50),
        }
    }

    actual = system.get_state()
    evaluate_state(expected, actual)
    assert actual == expected

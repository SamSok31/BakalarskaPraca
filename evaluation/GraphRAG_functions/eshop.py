from typing import Dict, Optional, Tuple


class Item:
    def __init__(self, label: str, cost: float, qty: int):
        self.label = label
        self.cost = cost
        self.qty = qty

    def __repr__(self):
        return f"Product(name={self.label}, price={self.cost}, stock={self.qty})"


class Client:
    def __init__(self, cid: str):
        self.cid = cid
        self.basket: Dict[str, int] = {}
        self.hold: Dict[str, int] = {}

    def __repr__(self):
        return f"User(id={self.cid}, cart={self.basket}, reservations={self.hold})"


class Purchase:
    def __init__(
        self,
        pid: str,
        cid: str,
        entries: Dict[str, Tuple[int, float]],
        state: str = "pending",
    ):
        self.pid = pid
        self.cid = cid
        self.entries = entries
        self.state = state

    def __repr__(self):
        return f"Order(id={self.pid}, user_id={self.cid}, products={self.entries}, status={self.state})"


class ShopEngine:
    def __init__(self):
        self._clients: Dict[str, Client] = {}
        self._catalog: Dict[str, Item] = {}
        self._purchases: Dict[str, Purchase] = {}
        self._seq = 1

    def create_user(self, uid: str) -> None:
        if uid not in self._clients:
            self._clients[uid] = Client(uid)

    def delete_user(self, uid: str) -> None:
        if uid not in self._clients:
            return

        person = self._clients[uid]
        for name, count in person.hold.items():
            if name in self._catalog:
                self._catalog[name].qty += count

        del self._clients[uid]

    def add_product(self, label: str, cost: float, qty: int) -> None:
        if qty < 0:
            return

        if label in self._catalog:
            entry = self._catalog[label]
            entry.qty += qty
            entry.cost = cost
        else:
            self._catalog[label] = Item(label, cost, qty)

    def delete_product(self, label: str) -> None:
        self._catalog.pop(label, None)

    def add_to_cart(self, uid: str, label: str, count: int) -> None:
        if uid not in self._clients or label not in self._catalog or count <= 0:
            return

        person = self._clients[uid]
        entry = self._catalog[label]

        if entry.qty < count:
            return

        person.basket[label] = person.basket.get(label, 0) + count
        person.hold[label] = person.hold.get(label, 0) + count
        entry.qty -= count

    def remove_from_cart(self, uid: str, label: str, count: int) -> None:
        if uid not in self._clients or label not in self._catalog or count <= 0:
            return

        person = self._clients[uid]

        if label not in person.basket or person.basket[label] < count:
            return

        person.basket[label] -= count
        if person.basket[label] == 0:
            del person.basket[label]

        if label in person.hold and person.hold[label] >= count:
            person.hold[label] -= count
            if person.hold[label] == 0:
                del person.hold[label]

            if label in self._catalog:
                self._catalog[label].qty += count

    def checkout(self, uid: str) -> Optional[str]:
        if uid not in self._clients or not self._clients[uid].basket:
            return None

        person = self._clients[uid]
        compiled: Dict[str, Tuple[int, float]] = {}

        for label, count in person.basket.items():
            if label not in self._catalog:
                return None
            compiled[label] = (count, self._catalog[label].cost)

        pid = f"SK{self._seq:05d}"
        self._seq += 1

        self._purchases[pid] = Purchase(pid, uid, compiled)

        person.basket.clear()
        person.hold.clear()

        return pid

    def update_order_status(self, pid: str, new_state: str) -> None:
        if pid not in self._purchases:
            return

        purchase = self._purchases[pid]

        if new_state == "cancelled" and purchase.state != "cancelled":
            purchase.state = "cancelled"

            for label, (count, cost) in purchase.entries.items():
                if label in self._catalog:
                    self._catalog[label].qty += count
                else:
                    self._catalog[label] = Item(label, cost, count)
            return

        transitions = {
            "pending": ["processing"],
            "processing": ["completed"],
            "completed": ["shipped"],
            "shipped": ["delivered"],
            "delivered": [],
            "cancelled": [],
        }

        if new_state in transitions[purchase.state]:
            purchase.state = new_state

    def get_state(self) -> Dict:
        return {
            "users": self._clients,
            "products": self._catalog,
            "orders": self._purchases,
            "available_stock": {
                k: v.qty for k, v in self._catalog.items()
            },
        }

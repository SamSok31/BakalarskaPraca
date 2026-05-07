#TODO: Choose the correct adapter to connect the generated code with the tests
from reservation_system_RooCode.adapter1 import ReservationSystem

from evaluation import evaluate_state


# A) USERS

def test_A1_create_user():
    system = ReservationSystem()

    system.create_user("A")

    expected = {
        "users": {"A"},
        "rooms": set(),
        "reservations": set() }

    actual = {
        "users": system.users,
        "rooms": system.rooms,
        "reservations": system.reservations }

    evaluate_state(expected, actual)
    assert actual == expected


def test_A2_delete_user_without_reservations():
    system = ReservationSystem()

    system.create_user("A")
    system.delete_user("A")

    expected = {
        "users": set(),
        "rooms": set(),
        "reservations": set() }

    actual = {
        "users": system.users,
        "rooms": system.rooms,
        "reservations": system.reservations }

    evaluate_state(expected, actual)
    assert actual == expected


def test_A3_delete_user_with_reservations():
    system = ReservationSystem()

    system.create_user("A")
    system.create_room("R1")
    system.create_reservation("A", "R1")
    system.delete_user("A")

    expected = {
        "users": set(),
        "rooms": {"R1"},
        "reservations": set() }

    actual = {
        "users": system.users,
        "rooms": system.rooms,
        "reservations": system.reservations }

    evaluate_state(expected, actual)
    assert actual == expected


def test_A4_duplicate_user():
    system = ReservationSystem()

    system.create_user("A")
    system.create_user("A")

    expected = {
        "users": {"A"},
        "rooms": set(),
        "reservations": set() }

    actual = {
        "users": system.users,
        "rooms": system.rooms,
        "reservations": system.reservations }

    evaluate_state(expected, actual)
    assert actual == expected


def test_A5_delete_non_existing_user():
    system = ReservationSystem()

    system.delete_user("A")

    expected = {
        "users": set(),
        "rooms": set(),
        "reservations": set() }

    actual = {
        "users": system.users,
        "rooms": system.rooms,
        "reservations": system.reservations }

    evaluate_state(expected, actual)
    assert actual == expected


def test_A6_delete_one_user_does_not_affect_others():
    system = ReservationSystem()

    system.create_user("A")
    system.create_user("B")
    system.delete_user("A")

    expected = {
        "users": {"B"},
        "rooms": set(),
        "reservations": set() }

    actual = {
        "users": system.users,
        "rooms": system.rooms,
        "reservations": system.reservations }

    evaluate_state(expected, actual)
    assert actual == expected


def test_A7_delete_user_with_multiple_reservations():
    system = ReservationSystem()

    system.create_user("A")
    system.create_room("R1")
    system.create_room("R2")
    system.create_reservation("A", "R1")
    system.create_reservation("A", "R2")
    system.delete_user("A")

    expected = {
        "users": set(),
        "rooms": {"R1", "R2"},
        "reservations": set() }

    actual = {
        "users": system.users,
        "rooms": system.rooms,
        "reservations": system.reservations }

    evaluate_state(expected, actual)
    assert actual == expected



# B) ROOMS

def test_B1_create_room():
    system = ReservationSystem()

    system.create_room("R1")

    expected = {
        "users": set(),
        "rooms": {"R1"},
        "reservations": set() }

    actual = {
        "users": system.users,
        "rooms": system.rooms,
        "reservations": system.reservations }

    evaluate_state(expected, actual)
    assert actual == expected


def test_B2_delete_room_without_reservation():
    system = ReservationSystem()

    system.create_room("R1")
    system.delete_room("R1")

    expected = {
        "users": set(),
        "rooms": set(),
        "reservations": set() }

    actual = {
        "users": system.users,
        "rooms": system.rooms,
        "reservations": system.reservations }

    evaluate_state(expected, actual)
    assert actual == expected


def test_B3_delete_room_with_reservation():
    system = ReservationSystem()

    system.create_user("A")
    system.create_room("R1")
    system.create_reservation("A", "R1")
    system.delete_room("R1")

    expected = {
        "users": {"A"},
        "rooms": set(),
        "reservations": set() }

    actual = {
        "users": system.users,
        "rooms": system.rooms,
        "reservations": system.reservations }

    evaluate_state(expected, actual)
    assert actual == expected


def test_B4_duplicate_room():
    system = ReservationSystem()

    system.create_room("R1")
    system.create_room("R1")

    expected = {
        "users": set(),
        "rooms": {"R1"},
        "reservations": set() }

    actual = {
        "users": system.users,
        "rooms": system.rooms,
        "reservations": system.reservations }

    evaluate_state(expected, actual)
    assert actual == expected


def test_B5_delete_non_existing_room():
    system = ReservationSystem()

    system.delete_room("R1")

    expected = {
        "users": set(),
        "rooms": set(),
        "reservations": set() }

    actual = {
        "users": system.users,
        "rooms": system.rooms,
        "reservations": system.reservations }

    evaluate_state(expected, actual)
    assert actual == expected


def test_B6_delete_one_room_does_not_affect_others():
    system = ReservationSystem()

    system.create_room("R1")
    system.create_room("R2")
    system.delete_room("R1")

    expected = {
        "users": set(),
        "rooms": {"R2"},
        "reservations": set() }

    actual = {
        "users": system.users,
        "rooms": system.rooms,
        "reservations": system.reservations }

    evaluate_state(expected, actual)
    assert actual == expected


def test_B7_delete_room_with_multiple_reservations():
    system = ReservationSystem()

    system.create_user("A")
    system.create_user("B")
    system.create_room("R1")
    system.create_reservation("A", "R1")
    system.create_reservation("B", "R1")
    system.delete_room("R1")

    expected = {
        "users": {"A", "B"},
        "rooms": set(),
        "reservations": set() }

    actual = {
        "users": system.users,
        "rooms": system.rooms,
        "reservations": system.reservations }

    evaluate_state(expected, actual)
    assert actual == expected



# C) RESERVATIONS

def test_C1_basic_reservation():
    system = ReservationSystem()

    system.create_user("A")
    system.create_room("R1")
    system.create_reservation("A", "R1")

    expected = {
        "users": {"A"},
        "rooms": {"R1"},
        "reservations": {("A", "R1", None)} }

    actual = {
        "users": system.users,
        "rooms": system.rooms,
        "reservations": system.reservations }

    evaluate_state(expected, actual)
    assert actual == expected


def test_C2_double_booking():
    system = ReservationSystem()

    system.create_user("A")
    system.create_user("B")
    system.create_room("R1")
    system.create_reservation("A", "R1")
    system.create_reservation("B", "R1")

    expected = {
        "users": {"A", "B"},
        "rooms": {"R1"},
        "reservations": {("A", "R1", None)} }

    actual = {
        "users": system.users,
        "rooms": system.rooms,
        "reservations": system.reservations }

    evaluate_state(expected, actual)
    assert actual == expected


def test_C3_cancel_reservation():
    system = ReservationSystem()

    system.create_user("A")
    system.create_room("R1")
    system.create_reservation("A", "R1")
    system.cancel_reservation("A", "R1")

    expected = {
        "users": {"A"},
        "rooms": {"R1"},
        "reservations": set() }

    actual = {
        "users": system.users,
        "rooms": system.rooms,
        "reservations": system.reservations }

    evaluate_state(expected, actual)
    assert actual == expected


def test_C4_cancel_non_existing():
    system = ReservationSystem()

    system.create_user("A")
    system.create_room("R1")
    system.cancel_reservation("A", "R1")

    expected = {
        "users": {"A"},
        "rooms": {"R1"},
        "reservations": set() }

    actual = {
        "users": system.users,
        "rooms": system.rooms,
        "reservations": system.reservations }

    evaluate_state(expected, actual)
    assert actual == expected


def test_C5_recreate_after_cancel():
    system = ReservationSystem()

    system.create_user("A")
    system.create_room("R1")
    system.create_reservation("A", "R1")
    system.cancel_reservation("A", "R1")
    system.create_reservation("A", "R1")

    expected = {
        "users": {"A"},
        "rooms": {"R1"},
        "reservations": {("A", "R1", None)} }

    actual = {
        "users": system.users,
        "rooms": system.rooms,
        "reservations": system.reservations }

    evaluate_state(expected, actual)
    assert actual == expected


def test_C6_reservation_without_user():
    system = ReservationSystem()

    system.create_room("R1")
    system.create_reservation("A", "R1")

    expected = {
        "users": set(),
        "rooms": {"R1"},
        "reservations": set() }

    actual = {
        "users": system.users,
        "rooms": system.rooms,
        "reservations": system.reservations }

    evaluate_state(expected, actual)
    assert actual == expected


def test_C7_reservation_without_room():
    system = ReservationSystem()

    system.create_user("A")
    system.create_reservation("A", "R1")

    expected = {
        "users": {"A"},
        "rooms": set(),
        "reservations": set() }

    actual = {
        "users": system.users,
        "rooms": system.rooms,
        "reservations": system.reservations }

    evaluate_state(expected, actual)
    assert actual == expected


def test_C8_duplicate_reservation():
    system = ReservationSystem()

    system.create_user("A")
    system.create_room("R1")
    system.create_reservation("A", "R1")
    system.create_reservation("A", "R1")

    expected = {
        "users": {"A"},
        "rooms": {"R1"},
        "reservations": {("A", "R1", None)} }

    actual = {
        "users": system.users,
        "rooms": system.rooms,
        "reservations": system.reservations }

    evaluate_state(expected, actual)
    assert actual == expected


def test_C9_cancel_one_among_many():
    system = ReservationSystem()

    system.create_user("A")
    system.create_room("R1")
    system.create_room("R2")

    system.create_reservation("A", "R1")
    system.create_reservation("A", "R2")

    system.cancel_reservation("A", "R1")

    expected = {
        "users": {"A"},
        "rooms": {"R1", "R2"},
        "reservations": {("A", "R2", None)} }

    actual = {
        "users": system.users,
        "rooms": system.rooms,
        "reservations": system.reservations }

    evaluate_state(expected, actual)
    assert actual == expected



# D) EDGE CASES

def test_D1_multiple_cancels():
    system = ReservationSystem()

    system.create_user("A")
    system.create_room("R1")
    system.create_reservation("A", "R1")
    system.cancel_reservation("A", "R1")
    system.cancel_reservation("A", "R1")

    expected = {
        "users": {"A"},
        "rooms": {"R1"},
        "reservations": set() }

    actual = {
        "users": system.users,
        "rooms": system.rooms,
        "reservations": system.reservations }

    evaluate_state(expected, actual)
    assert actual == expected


def test_D2_reservation_after_room_deletion():
    system = ReservationSystem()

    system.create_user("A")
    system.create_room("R1")
    system.delete_room("R1")
    system.create_reservation("A", "R1")

    expected = {
        "users": {"A"},
        "rooms": set(),
        "reservations": set() }

    actual = {
        "users": system.users,
        "rooms": system.rooms,
        "reservations": system.reservations }

    evaluate_state(expected, actual)
    assert actual == expected


def test_D3_cancel_after_room_deletion():
    system = ReservationSystem()

    system.create_user("A")
    system.create_room("R1")
    system.create_reservation("A", "R1")
    system.delete_room("R1")
    system.cancel_reservation("A", "R1")

    expected = {
        "users": {"A"},
        "rooms": set(),
        "reservations": set() }

    actual = {
        "users": system.users,
        "rooms": system.rooms,
        "reservations": system.reservations }

    evaluate_state(expected, actual)
    assert actual == expected


def test_D4_cancel_after_user_deletion():
    system = ReservationSystem()

    system.create_user("A")
    system.create_room("R1")
    system.create_reservation("A", "R1")
    system.delete_user("A")
    system.cancel_reservation("A", "R1")

    expected = {
        "users": set(),
        "rooms": {"R1"},
        "reservations": set() }

    actual = {
        "users": system.users,
        "rooms": system.rooms,
        "reservations": system.reservations }

    evaluate_state(expected, actual)
    assert actual == expected



# E) COMPLEX SCENÁRE

def test_E1_loop_booking():
    system = ReservationSystem()

    system.create_room("R1")
    system.create_user("A")
    system.create_user("B")
    system.create_user("C")

    for user in ["A", "B", "C"]:
        system.create_reservation(user, "R1")

    expected = {
        "users": {"A", "B", "C"},
        "rooms": {"R1"},
        "reservations": {("A", "R1", None)} }

    actual = {
        "users": system.users,
        "rooms": system.rooms,
        "reservations": system.reservations }

    evaluate_state(expected, actual)
    assert actual == expected


def test_E2_multiple_rooms():
    system = ReservationSystem()

    system.create_user("A")
    system.create_room("R1")
    system.create_room("R2")
    system.create_room("R3")

    for room in ["R1", "R2", "R3"]:
        system.create_reservation("A", room)

    expected = {
        "users": {"A"},
        "rooms": {"R1", "R2", "R3"},
        "reservations": {
            ("A", "R1", None),
            ("A", "R2", None),
            ("A", "R3", None) } }

    actual = {
        "users": system.users,
        "rooms": system.rooms,
        "reservations": system.reservations }

    evaluate_state(expected, actual)
    assert actual == expected


def test_E3_mixed_operations():
    system = ReservationSystem()

    system.create_user("A")
    system.create_user("B")
    system.create_room("R1")
    system.create_room("R2")

    system.create_reservation("A", "R1")
    system.create_reservation("B", "R2")

    system.cancel_reservation("A", "R1")
    system.create_reservation("B", "R1")

    expected = {
        "users": {"A", "B"},
        "rooms": {"R1", "R2"},
        "reservations": {
            ("B", "R1", None),
            ("B", "R2", None) } }

    actual = {
        "users": system.users,
        "rooms": system.rooms,
        "reservations": system.reservations }

    evaluate_state(expected, actual)
    assert actual == expected


def test_E4_deletion_impact():
    system = ReservationSystem()

    system.create_user("A")
    system.create_user("B")
    system.create_room("R1")
    system.create_room("R2")

    system.create_reservation("A", "R1")
    system.create_reservation("B", "R2")

    system.delete_user("A")

    expected = {
        "users": {"B"},
        "rooms": {"R1", "R2"},
        "reservations": {("B", "R2", None)} }

    actual = {
        "users": system.users,
        "rooms": system.rooms,
        "reservations": system.reservations }

    evaluate_state(expected, actual)
    assert actual == expected


def test_E5_stress_scenario():
    system = ReservationSystem()

    system.create_user("A")
    system.create_user("B")
    system.create_user("C")
    system.create_room("R1")
    system.create_room("R2")

    for user in ["A", "B", "C"]:
        for room in ["R1", "R2"]:
            system.create_reservation(user, room)

    expected = {
        "users": {"A", "B", "C"},
        "rooms": {"R1", "R2"},
        "reservations": {
            ("A", "R1", None),
            ("A", "R2", None) } }

    actual = {
        "users": system.users,
        "rooms": system.rooms,
        "reservations": system.reservations }

    evaluate_state(expected, actual)
    assert actual == expected



# F) TIME-AWARE SCENÁRE

def test_F1_non_overlapping_reservations():
    system = ReservationSystem()

    system.create_user("A")
    system.create_user("B")
    system.create_room("R1")

    system.create_reservation("A", "R1", time=(10, 11))
    system.create_reservation("B", "R1", time=(11, 12))

    expected = {
        "users": {"A", "B"},
        "rooms": {"R1"},
        "reservations": {
            ("A", "R1", (10, 11)),
            ("B", "R1", (11, 12)) } }

    actual = {
        "users": system.users,
        "rooms": system.rooms,
        "reservations": system.reservations }

    evaluate_state(expected, actual)
    assert actual == expected


def test_F2_overlapping_reservations():
    system = ReservationSystem()

    system.create_user("A")
    system.create_user("B")
    system.create_room("R1")

    system.create_reservation("A", "R1", time=(10, 12))
    system.create_reservation("B", "R1", time=(11, 13))

    expected = {
        "users": {"A", "B"},
        "rooms": {"R1"},
        "reservations": {
            ("A", "R1", (10, 12)) } }

    actual = {
        "users": system.users,
        "rooms": system.rooms,
        "reservations": system.reservations }

    evaluate_state(expected, actual)
    assert actual == expected


def test_F3_reuse_time_after_cancel():
    system = ReservationSystem()

    system.create_user("A")
    system.create_user("B")
    system.create_room("R1")

    system.create_reservation("A", "R1", time=(10, 12))
    system.cancel_reservation("A", "R1", time=(10, 12))
    system.create_reservation("B", "R1", time=(10, 12))

    expected = {
        "users": {"A", "B"},
        "rooms": {"R1"},
        "reservations": {
            ("B", "R1", (10, 12)) } }

    actual = {
        "users": system.users,
        "rooms": system.rooms,
        "reservations": system.reservations }

    evaluate_state(expected, actual)
    assert actual == expected


def test_F4_boundary_overlap():
    system = ReservationSystem()

    system.create_user("A")
    system.create_user("B")
    system.create_room("R1")

    system.create_reservation("A", "R1", time=(10, 11))
    system.create_reservation("B", "R1", time=(11, 12))

    expected = {
        "users": {"A", "B"},
        "rooms": {"R1"},
        "reservations": {
            ("A", "R1", (10, 11)),
            ("B", "R1", (11, 12)) } }

    actual = {
        "users": system.users,
        "rooms": system.rooms,
        "reservations": system.reservations }

    evaluate_state(expected, actual)
    assert actual == expected

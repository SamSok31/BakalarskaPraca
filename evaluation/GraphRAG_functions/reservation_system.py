class ReservationUtils:

    @staticmethod
    def is_room_available(reservations, room):
        if room is None:
            return False

        return all(r[1] != room for r in reservations)


    @staticmethod
    def add_reservation(reservations, user, room):
        if user is None or room is None:
            return False

        if not ReservationUtils.is_room_available(reservations, room):
            return False

        reservations.add((user, room))
        return True


    @staticmethod
    def cancel_reservation(reservations, user, room):
        if (user, room) in reservations:
            reservations.remove((user, room))
            return True

        return False


    @staticmethod
    def remove_user_reservations(reservations, user):
        return {r for r in reservations if r[0] != user}


    @staticmethod
    def transfer_reservation(reservations, from_user, to_user, room):
        if (from_user, room) not in reservations:
            return False

        if not ReservationUtils.is_room_available(reservations - {(from_user, room)}, room):
            return False

        reservations.remove((from_user, room))
        reservations.add((to_user, room))

        return True


    @staticmethod
    def bulk_reserve(reservations, user, rooms):
        reserved = []

        for room in rooms:
            if ReservationUtils.is_room_available(reservations, room):
                reservations.add((user, room))
                reserved.append(room)

        return reserved

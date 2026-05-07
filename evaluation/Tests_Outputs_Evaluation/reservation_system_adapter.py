#TODO: Choose the correct generated code to import
from reservation_system_RooCode.output1 import ReservationSystem as GeneratedSystem

class ReservationSystem:
    
    def __init__(self):
        self.system = GeneratedSystem()

    
    def create_user(self, user_id: str):
        raise NotImplementedError

    def delete_user(self, user_id: str):
        raise NotImplementedError

    
    def create_room(self, room_id: str):
        raise NotImplementedError

    def delete_room(self, room_id: str):
        raise NotImplementedError


    def create_reservation(self, user_id: str, room_id: str, time=None):
        raise NotImplementedError

    def cancel_reservation(self, user_id: str, room_id: str, time=None):
        raise NotImplementedError
    

    def get_state(self):
        raise NotImplementedError

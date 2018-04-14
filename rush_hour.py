import numpy as np
import random
        
class Person(object):
    def __init__(self,arrival_time):
        self.elevator_wait = 0
        self.lobby_wait = 0
        self.arrival_time = arrival_time
        self.desired_floor = random.randrange(0,12)
        
    def board(self, elevator, time):
        self.lobby_wait = time - self.arrival_time
        elevator.passengers.append(self)
        if self.desired_floor not in elevator.selected_floors:
            elevator.selected_floors.append(self.desired_floor)

    def depart(self, elevator, time):
        self.elevator_wait = time - self.arrival_time
        elevator.passengers.remove(self)
        
class Elevator(object):
    def __init__(self, max_load = 6):
        self.max_load = max_load #(can be tweaked, doors will shut instantly if max load is reached)
        self.current_load = 0
        self.door_close_time = 15
        self.selected_floors = []   #
        self.passengers = []        #list of passengers on board
        self.floor = 1              #floor elevator is currently on
        self.door_open = True       #boolean, whether or not elevator can accept new passengers

    def ascend(self,time):
        pass

    
class Floor(object):
    def __init__(self,):
        #self.number = number #could just track this as an array index... probably faster than a search every time a floor is selected.
        self.elevators = []

class Lobby(object):
    def __init__(self, ):
        self.passengers = []
              
def new_passenger(time):
    delay = random.random()*30
    a_time = time + delay
    return Person(a_time)

def get_soonest_door_close(elevators):
    sdc = 15.
    sdce = elevators[0]
    for e in elevators:
        if e.door_close_time < sdc:
            sdc = e.door_close_time
            sdce = e
    return sdc, sdce

def main():
    time = 0
    elevators = [Elevator() for i in range(0,4)]
    floors = [Floor() for i in range(0,12)]
    while time <= 1000:
        p = new_passenger(time)
        [sdc, sdce] = get_soonest_door_close(elevators)
        if sdc < p.arrival_time:
            time += sdc
            sdce.ascend(time)
        for e in elevators:
            if e.floor==1 and e.current_load < e.max_load:
                pass

elevators = [Elevator() for i in range(0,4)]
[sdc, sdce] = get_soonest_door_close(elevators)
print(sdc)

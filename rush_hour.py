import numpy as np
import random
#TO-DO
#remove globals?
#split this thing into multiple files cause its fat af
#make main() actually function

#HUGE
#possibly implement two queues: one for passenger arrivals, and another (more flexible) for elevator door closes and departures etc.
#would need a method to decide which one will trigger an event first

#SHITTY GLOBAL VARIABLES
total_passengers_delivered = 0
total_elevator_wait_time = 0
total_lobby_wait_time = 0
#/SHITTY VARIABLES

class Stats(object): #maybe use this to track stats instead of the shitty globals i'm using above
    def __init__(self):
        total_passengers_delivered = 0
        total_elevator_wait_time = 0
        total_lobby_wait_time = 0

        
class PQ(object): #priority queue, with time events represented as a tuple (action, time to event). Time to event is in t-minus style.
    def __init__(self):
        self.queue = []

    def push(self, event):
        inserted = False
        i = 0
        for item in self.queue:
            if item[1] > event[1]:
                self.queue.insert(i,event)
                inserted = True
            i+=1
        if inserted == False:
            self.queue.append(event)
            
    def pop(self):
        return self.queue.pop(0)
    
        
class EventQueue(object):
    def __init__(self):
        self.events = PQ()
        self.time = 0.

    def add_event(self, event):
        self.events.push(event)

    def get_next_event(self):
        popped_event = self.events.pop()
        self.time += popped_event[1]
        return self.events.pop()

    
class Person(object):
    def __init__(self,arrival_time):
        self.elevator_wait = 0.
        self.lobby_wait = 0.
        self.arrival_time = arrival_time
        self.desired_floor = random.randrange(0,12)
        
    def board(self, elevator, time):
        self.lobby_wait = time - self.arrival_time
        elevator.passengers.append(self)
        if self.desired_floor not in elevator.selected_floors:
            elevator.selected_floors.append(self.desired_floor)

    def depart(self, elevator, time):
        self.elevator_wait = time - self.arrival_time
        total_passengers_delivered += 1
        total_elevator_wait_time += self.elevator_wait
        total_lobby_wait_time += self.lobby_wait

        
class Elevator(object):
    def __init__(self, identifier, max_load = 6):
        self.max_load = max_load #can be tweaked, doors will shut instantly if max load is reached)
        self.identifier = identifier #we will see if this is needed... probly not since I can just pass self.departure()
        self.current_load = 0
        self.door_close_time = 15.
        self.selected_floors = []   
        self.passengers = []        #list of passengers on board

    def ascend(self, events, time):
        self.door_close_time = 0
        elevator_ride_time =  5.*len(self.selected_floors)          #5 seconds of stopping per floor
        elevator_ride_time += 3.*(max(self.selected_floors) + 1)    #3 seconds per floor we need to travel
        events.add_event((self.departure(time + elevator_ride_time), elevator_ride_time))

    def departure(self, time):
        for passenger in self.passengers:
            passenger.depart(self, time - 3.*(max(self.selected_floors) - passenger.desired_floor))
        #reset everything in the elevator to 0, assume it instantly returns to ground floor (change "ascend" if disagree)
        self.current_load = 0
        self.door_close_time = 15.
        self.selected_floors = []
        self.passengers = []


class Lobby(object):
    def __init__(self, ):
        self.passengers = []

              
def new_passenger(time):
    p = Person(time)
    #some code on "if elevator[i] is open, board instantly"


def get_soonest_door_close(elevators): #this probably isn't needed since we have an event queue
    sdc = 15.
    sdce = elevators[0]
    for e in elevators:
        if e.door_close_time < sdc:
            sdc = e.door_close_time
            sdce = e.identifier
    return sdc, sdce


def main(RUN_TIME = 10000):
    time = 0
    elevators = [Elevator(i) for i in range(0,4)]
    events = EventQueue()
    while time <= RUN_TIME: #push all passenger generation events first
        delay = random.random()*30.
        events.push((new_passenger(time + delay), delay))
        time += delay
        

elevators = [Elevator() for i in range(0,4)]
[sdc, sdce] = get_soonest_door_close(elevators)
print(sdc)





'''
class Floor(object): #probably dont even need this class...
    def __init__(self,):
        #self.number = number #could just track this as an array index... probably faster than a search every time a floor is selected.
        self.elevators = []
'''
'''
while time <= 1000:
        p = new_passenger(time)
        [sdc, sdce] = get_soonest_door_close(elevators)
        if sdc < p.arrival_time:
            time += sdc
            sdce.ascend(time)
        for e in elevators:
            if e.floor==1 and e.current_load < e.max_load:
                pass
'''



















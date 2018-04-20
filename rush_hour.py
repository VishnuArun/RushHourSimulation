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
        
class EventQueue(object):
    def __init__(self):
        self.queue = []
        #self.time = 0.

    def add_right(self, event):
        self.queue.append(event)
        
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

    def get_soonest(self):
        if len(self.queue) > 0:
            return self.queue[0][1]
        else:
            return 10000000
    
class Person(object):
    def __init__(self,arrival_time,events):
        self.elevator_wait = 0.
        self.lobby_wait = 0.
        self.arrival_time = arrival_time
        self.events = events
        self.desired_floor = random.randrange(0,12)
        
    def board(self, elevator, time):
        self.lobby_wait = time - self.arrival_time
        elevator.passengers.append(self)
        elevator.current_load += 1
        elevator.door_close_time = 15.
        if self.desired_floor not in elevator.selected_floors:
            elevator.selected_floors.append(self.desired_floor)
        if elevator.current_load == elevator.max_load:
            elevator.ascend(self.events, time)

    def depart(self, elevator, time):
        global total_passengers_delivered
        global total_elevator_wait_time
        global total_lobby_wait_time
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
        if self.selected_floors == []:
            events.push((self.identifier, 0))
        else:
            self.door_close_time = -1
            elevator_ride_time =  5.*len(self.selected_floors)          #5 seconds of stopping per floor
            elevator_ride_time += 3.*(max(self.selected_floors) + 1)    #3 seconds per floor we need to travel
            events.push((self.identifier, elevator_ride_time + time))

    def depart(self, time):
        if self.selected_floors == []:
            self.current_load = 0
            self.door_close_time = 15.
            self.selected_floors = []
            self.passengers = []
            return
        
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
        
    def add(self, passenger):
        self.passengers.append(passenger)

              
def new_passenger(lobby, time):
    lobby.add(Person(time))

def get_soonest_door_close(elevators): 
    sdc = 15.
    sdce = 0
    for e in elevators:
        if (e.door_close_time > 0) and (e.door_close_time < sdc):
            sdc = e.door_close_time
            sdce = e.identifier
    return sdc, sdce


def main(RUN_TIME = 1000):
    virtual_time = 0
    elevators = [Elevator(i) for i in range(0,4)]
    passenger_spawn_events = []
    lobby = []
    while virtual_time <= RUN_TIME: #push all passenger generation events first
        delay = random.random()*30.
        passenger_spawn_events.append(virtual_time + delay)
        virtual_time += delay
    LENGTH = len(passenger_spawn_events)
    time = 0
    events = EventQueue()
    while time <= RUN_TIME:
        for passenger in lobby:
            for elevator in elevators:
                if elevator.door_close_time != 0:
                    passenger.board(elevator, time)
                    break
        [sdc, sdce] = get_soonest_door_close(elevators)
        #print(events.get_soonest())
        if sdc == min(sdc, events.get_soonest() - time, passenger_spawn_events[0] - time):
            time += sdc
            elevators[sdce].ascend(events,time)
            
        elif passenger_spawn_events[0] - time == min(sdc, events.get_soonest() - time, passenger_spawn_events[0] - time):
            time = passenger_spawn_events.pop(0)
            lobby.append(Person(time,events))
            
        else:
            #print(events.queue)
            event = events.pop()
            time += event[1]
            elevators[event[0]].depart(time)
            
        print(time)
    print('Total Passengers Delivered: '+str(total_passengers_delivered))
    print('Supposed number of passengers: '+str(LENGTH))
    print('Total Elevator Wait Time: '+str(total_elevator_wait_time))
    print('Total Lobby Wait Time: '+str(total_lobby_wait_time))
    
    

#elevators = [Elevator(i) for i in range(0,4)]
#elevators[1].door_close_time=14.
#[sdc, sdce] = get_soonest_door_close(elevators)
#print(sdc,sdce)
main()




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



















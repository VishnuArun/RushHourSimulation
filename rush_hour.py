import numpy as np
import random
import math

#TO-DO
#remove globals?
#split this thing into multiple files cause its fat af


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
                break
            i+=1
        if inserted == False:
            self.queue.append(event)
            
    def pop(self):
        return self.queue.pop(0)

    def get_soonest(self):
        if len(self.queue) > 0:
            return self.queue[0][1]
        else:
            return float('inf')
    
class Person(object):
    def __init__(self,arrival_time):
        self.elevator_wait = 0.
        self.lobby_wait = 0.
        self.arrival_time = arrival_time
        self.desired_floor = random.randrange(0,12)

        #DEBUG
        self.count = 0
        
    def board(self, elevator, events, time):
        self.lobby_wait = time - self.arrival_time
        elevator.passengers.append(self)
        elevator.current_load += 1
        elevator.door_close_time = 15.
        if self.desired_floor not in elevator.selected_floors:
            elevator.selected_floors.append(self.desired_floor)
        if elevator.current_load >= elevator.max_load:
            elevator.ascend(events, time)
            elevator.door_close_time = float('inf')

    def depart(self, elevator, time):
        global total_passengers_delivered
        global total_elevator_wait_time
        global total_lobby_wait_time
        elevator.current_load -= 1
        self.elevator_wait = time - self.arrival_time
        total_passengers_delivered += 1
        total_elevator_wait_time += self.elevator_wait
        total_lobby_wait_time += self.lobby_wait

        #DEBUG
        self.count+=1
        if self.count>1:
            print('I have been deboarded '+str(self.count)+' times')

        
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
            #print("Elevator "+str(self.identifier)+" ascending with "+str(self.current_load))
            #events.push((self.identifier, time))
            return
        else:
            print("Elevator "+str(self.identifier)+" ascending with "+str(self.current_load))
            #print("Load: "+str(self.passengers))
            self.door_close_time = float('inf')
            elevator_ride_time =  5.*len(self.selected_floors)          #5 seconds of stopping per floor
            elevator_ride_time += 3.*(max(self.selected_floors) + 1)    #3 seconds per floor we need to travel
            events.push((self.identifier, elevator_ride_time + time))
            

    def deboard(self, time):
        if self.selected_floors == []:
            self.current_load = 0
            self.door_close_time = 15.
            self.selected_floors = []
            self.passengers = []
            return
        i=0
        for passenger in self.passengers:
            travel_adjustment = 3.*(max(self.selected_floors) - passenger.desired_floor)
            stop_adjustment = 0
            for floor in self.selected_floors:
                if floor >= passenger.desired_floor:
                    stop_adjustment += 5
            passenger.depart(self, time - stop_adjustment - travel_adjustment)
            i+=1
        #reset everything in the elevator to 0, assume it instantly returns to ground floor (change "ascend" if disagree)
        self.current_load = 0
        self.door_close_time = 15.
        self.selected_floors = []
        self.passengers = []
        
        print("Elevator "+str(self.identifier)+" returned to ground after dumping "+str(i))


class Lobby(object):
    def __init__(self, ):
        self.passengers = []
        
    def add(self, passenger):
        self.passengers.append(passenger)

              
def new_passenger(lobby, time):
    lobby.add(Person(time))

def not_empty(elevators):
    for e in elevators:
        if e.passengers != []:
            return True
def decrement_door_close_times(elevators, events, time, adjustment):
    for e in elevators:
        e.door_close_time -= adjustment
        if e.door_close_time < 0:
            e.door_close_time = 0
        if e.door_close_time < 10**-8:
            events.push((e.identifier, time))
        
def get_soonest_door_close(elevators): 
    sdc = 15.
    sdce = 0
    for e in elevators:
        if (e.door_close_time < sdc):
            sdc = e.door_close_time
            sdce = e.identifier
    return sdc, sdce


def main(RUN_TIME = 10000):
    virtual_time = 0
    elevators = [Elevator(i) for i in range(0,4)]
    passenger_spawn_events = []
    lobby = []
    while virtual_time <= RUN_TIME: #push all passenger generation events first
        delay = random.random()*5.
        passenger_spawn_events.append(virtual_time + delay)
        virtual_time += delay
    LENGTH = len(passenger_spawn_events)
    passenger_spawn_events.append(float('inf')) 
    time = 0
    events = EventQueue()
    while time <= RUN_TIME or lobby != [] or not_empty(elevators):
        for passenger in lobby:
            for elevator in elevators:
                if elevator.door_close_time <= 15:
                    passenger.board(elevator, events, time)
                    lobby.remove(passenger)
                    #print('Person boarded elevator '+str(elevator.identifier)+' dct of '+str(elevator.door_close_time))
                    break
        [sdc, sdce] = get_soonest_door_close(elevators)
        oldtime = time
        #print(sdc, passenger_spawn_events[0] - time, events.get_soonest() - time)
        #print(events.queue)
        if events.get_soonest() - time == min(sdc, events.get_soonest() - time, passenger_spawn_events[0] - time):
            event = events.pop()
            time = event[1]
            elevators[event[0]].deboard(time)
           
        elif passenger_spawn_events[0] - time == min(sdc, events.get_soonest() - time, passenger_spawn_events[0] - time):
            time = passenger_spawn_events.pop(0)
            lobby.append(Person(time))
            #print(time)
            
        else:
            time += sdc
            elevators[sdce].ascend(events,time)
            #print(time)
            
            
        decrement_door_close_times(elevators, events, time, time - oldtime)   
        #print(time)
    print('Total Passengers Delivered: '+str(total_passengers_delivered))
    print('Supposed number of passengers: '+str(LENGTH))
    print('Total Elevator Wait Time: '+str(total_elevator_wait_time))
    print('Total Lobby Wait Time: '+str(total_lobby_wait_time))
    
    
def test():
    elevator = Elevator(0)
    events = EventQueue()
    time=0
    for i in range(0,6):
        p=Person(0)
        p.board(elevator,events,0)
    print(events.queue)
    print(elevator.selected_floors)
    print(sum(elevator.selected_floors))
    event = events.pop()
    time += event[1]
    elevator.deboard(time)
    print(time)
    print('Total Passengers Delivered: '+str(total_passengers_delivered))
    print('Supposed number of passengers: 6')
    print('Total Elevator Wait Time: '+str(total_elevator_wait_time))
    print('Total Lobby Wait Time: '+str(total_lobby_wait_time))


main()















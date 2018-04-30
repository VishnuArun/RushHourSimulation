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
        #print('Boarding dct: '+str(elevator.door_close_time))
        elevator.door_close_time = 15.
        if self.desired_floor not in elevator.selected_floors:
            elevator.selected_floors.append(self.desired_floor)
        if elevator.current_load > elevator.max_load:
            print('failure')


    def depart(self, elevator, time):
        global total_passengers_delivered
        global total_elevator_wait_time
        global total_lobby_wait_time
        elevator.current_load -= 1
        self.elevator_wait = time - self.arrival_time - self.lobby_wait
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
            self.door_close_time = 15.
            #print(self.passengers)
            #print("Elevator "+str(self.identifier)+" ascending with "+str(self.current_load))
            #events.push((self.identifier, time))
            return
        else:
            #print("Elevator "+str(self.identifier)+" ascending with "+str(self.current_load))
            #print("Load: "+str(self.passengers))
            self.door_close_time = float('inf')
            elevator_ride_time =  5.*len(self.selected_floors)          #5 seconds of stopping per floor
            elevator_ride_time += 3.*(max(self.selected_floors) + 1)    #3 seconds per floor we need to travel
            events.push((self.identifier, elevator_ride_time + time))
            

    def deboard(self, time):
        if self.selected_floors == []:
            self.current_load = 0
            #print('Deboarding dct: '+str(self.door_close_time))
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
        
        #print("Elevator "+str(self.identifier)+" returned to ground after dumping "+str(i))


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
            e.door_close_time = 0.
        #if e.door_close_time < 10**-8:
            #print('extra push')
            #e.ascend(events,time)
            #e.door_close_time = float('inf')
        
def get_soonest_door_close(elevators): 
    sdc = float('inf')
    sdce = 0
    for e in elevators:
        if (e.door_close_time < sdc):
            sdc = e.door_close_time
            sdce = e.identifier
    return sdc, sdce


def main(RUN_TIME,Max_Elevator):
    virtual_time = 0
    elevators = [Elevator(i) for i in range(0,Max_Elevator)]
    passenger_spawn_events = []
    lobby = []
    while virtual_time <= RUN_TIME: #generate all passenger generation events first
        delay = -math.log(1.0 - random.random())*5.
        passenger_spawn_events.append(virtual_time + delay)
        virtual_time += delay
    if passenger_spawn_events[-1] > RUN_TIME:
        passenger_spawn_events = passenger_spawn_events[:-1]
    LENGTH = len(passenger_spawn_events)
    passenger_spawn_events.append(float('inf')) 
    time = 0
    events = EventQueue()
    while time <= RUN_TIME or lobby != [] or not_empty(elevators):
        for passenger in lobby:
            for elevator in elevators:
                if (elevator.door_close_time <= 15) and (elevator.door_close_time > 0) and (elevator.current_load < elevator.max_load):
                    #print('Person boarded elevator '+str(elevator.identifier)+' dct of '+str(elevator.door_close_time))
                    passenger.board(elevator, events, time)
                    lobby.remove(passenger)
                    
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
            
        else:
            time += sdc
            elevators[sdce].ascend(events,time)
            

        decrement_door_close_times(elevators, events, time, time - oldtime)   

    #print('\nTotal Passengers Delivered: '+str(total_passengers_delivered))
    #print('Supposed number of passengers: '+str(LENGTH))
    #print('Avg Elevator Wait Time: '+str(total_elevator_wait_time/total_passengers_delivered))
    #print('Avg Lobby Wait Time: '+str(total_lobby_wait_time/total_passengers_delivered))
    return [total_passengers_delivered, LENGTH, total_elevator_wait_time, total_lobby_wait_time]
    

import matplotlib.pyplot as plt
import pandas as pd
ElevWaitTime = []
AvgElevWaitTime = 0
LobWaitTime = []
AvgLobWaitTime = 0
time = 4800 #number of seconds in the window from 7:50am to 9:10am, at least i think
trials = 100
for x in range(1,8):
    AvgElevWaitTime = 0
    AvgLobWaitTime = 0
    for y in range(0,trials):
        # reset global variables
        total_passengers_delivered = 0
        total_elevator_wait_time = 0
        total_lobby_wait_time = 0
        
        # call simulation
        t = main(time,x)
        #AvgElevWaitTime += t[2]
        #AvgLobWaitTime += t[3]
        #If we want the average time/passenger, use lines below
        #
        AvgElevWaitTime += t[2]/t[0]
        AvgLobWaitTime += t[3]/t[0]
        #
        
    ElevWaitTime.append([x,AvgElevWaitTime/trials])
    LobWaitTime.append([x,AvgLobWaitTime/trials])

    
dfW = pd.DataFrame(ElevWaitTime)
dfL = pd.DataFrame(LobWaitTime)
plt.plot(dfL[0], dfL[1], label = 'Lobby Wait Time')
plt.plot(dfW[0], dfW[1], label = 'Elevator Wait Time')

plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
plt.xlabel("Elevator")
plt.ylabel("Time (seconds)")
plt.title("Elevator Simulation")
print(" Using " + str(time) + " seconds per day, running over " + str(trials) + " trials ")
plt.show()






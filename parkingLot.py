
import argparse
import sys

from queue import PriorityQueue

from enum import Enum


class ErrorCode(Enum):
    NOTEXIST = -1
    CAPACITY_OVERFLOW = -2
    CAPACITY_UNDERFLOW = -3
    DUPLICATE_ENTRY = -4

class Driver:
    def __init__(self, age):
        self.age = age

class Vehicle:
    def __init__(self,regno,driver):
        self.driver =  driver
        self.regno = regno

class Car(Vehicle):
    def __init__(self,regno,driver):
        Vehicle.__init__(self,regno,driver)
    def getType(self):
        return "Car"


class Slot:
    def __init__(self, slotId, vehicle=None):
        self.slotId = slotId
        self.vehicle = vehicle

class ParkingLot:
    def __init__(self):
        self.capacity = 0
        self.numOfOccupiedSlots = 0
        self.slots = []
        self.vacantSlots = PriorityQueue()
        self.regno_parkingslot_mapping = {}

    def createParkingLot(self,capacity):
        if capacity <= 0:
            return ErrorCode.CAPACITY_UNDERFLOW

        self.capacity = capacity
        self.slots = [-1]*self.capacity

        for i in range(self.capacity):
            self.vacantSlots.put((i,Slot(i+1)))

        return self.capacity

    # Closest Vacant Slot
    def getVacantSlot(self):
        slot = self.vacantSlots.get()
        return slot[1]

    # Park Vehicle
    def park(self,vehicle):
        # check for duplicate entry
        if vehicle.regno in self.regno_parkingslot_mapping:
            return ErrorCode.DUPLICATE_ENTRY

        #check for parking lot capacity
        if self.numOfOccupiedSlots < self.capacity:
            # getting vacant slot object in 0(1)
            slot = self.getVacantSlot()

            # assigned vehicle to the slot
            slot.vehicle = vehicle
            
            #update vehicle registration number to slotId mapping
            self.regno_parkingslot_mapping[vehicle.regno] = slot.slotId

            #update slot Id to slot object mapping
            self.slots[slot.slotId-1] = slot

            self.numOfOccupiedSlots = self.numOfOccupiedSlots + 1
            
            return slot.slotId

        else:
            return ErrorCode.CAPACITY_OVERFLOW


    # Vehicle exit from Parking Lot
    def leave(self,slotId):
        # check if the mentioned slot has vehicle
        if self.numOfOccupiedSlots > 0 and self.slots[slotId-1] != -1:
            self.numOfOccupiedSlots = self.numOfOccupiedSlots - 1

            # getting registration number of vehicle
            regno = self.slots[slotId-1].vehicle.regno

            # removing VehicleRegistrationNumber to Slot ID mapping from mapping table
            self.regno_parkingslot_mapping.pop(regno)

            # getting slot object
            slot_obj = self.slots[slotId-1]

            # output object with the same data as of slot_obj
            output_obj = Slot(slotId,slot_obj.vehicle)

            # Removing vehicle from slot_obj
            slot_obj.vehicle = None

            # putting the slot_obj in vacant slots heap
            self.vacantSlots.put((slotId - 1,slot_obj))

            # slot is empty now
            self.slots[slotId-1] = -1

            return output_obj
        
        else:
            return ErrorCode.NOTEXIST

    # Slot for given Reg number
    def getSlotNoFromRegNo(self,regno):
        if regno in self.regno_parkingslot_mapping:
            return self.regno_parkingslot_mapping[regno]
        else:
            return ErrorCode.NOTEXIST

    # Slot Nos with given driver's age
    def getVehicleRegNosFromAge(self,age):
        regnos = []
        for i in range(self.capacity):
            if self.slots[i] != -1:
                if self.slots[i].vehicle.driver.age == age:
                    regnos.append(str(self.slots[i].vehicle.regno))
        if len(regnos) != 0:
            reg_nos = ', '.join(regnos)
            return reg_nos
        else:
            return ErrorCode.NOTEXIST

    # Slot Nos with given driver's Age
    def getSlotNosFromAge(self,age):
        slotnos = []
        for i in range(self.capacity):
            if self.slots[i] != -1:
                if self.slots[i].vehicle.driver.age == age:
                    slotnos.append(str(self.slots[i].slotId))
        if len(slotnos) != 0:
            slot_nos = ', '.join(slotnos)
            return slot_nos
        else:
            return ErrorCode.NOTEXIST

    # Execute all the given Instruction
    def executeInstructions(self,line,output):

        # Create Parking Lot
        if line.startswith('Create_parking_lot'):
            n = int(line.split(' ')[1])
            capacity = self.createParkingLot(n)
            if capacity != ErrorCode.CAPACITY_UNDERFLOW:
                print('Created parking of '+str(capacity)+' slots')
                output.write('Created parking of '+str(capacity)+' slots\n')
            else:
                print("Please enter valid capacity\n")
                sys.exit()

        # Parking of Vehicle
        elif line.startswith('Park'):
            regno = line.split(' ')[1]
            driver_age = line.split(' ')[3]
            driver = Driver(driver_age)
            vehicle = Car(regno,driver)
            slotno = self.park(vehicle)
            if slotno == ErrorCode.CAPACITY_OVERFLOW:
                print("Sorry, parking lot is full")
                output.write("Sorry, parking lot is full")
            elif slotno == ErrorCode.DUPLICATE_ENTRY:
                print("Car number with reg "+ str(regno) + "has alredy been parked")
                output.write("Car number with reg "+ str(regno) + "has alredy been parked")
            else:
                print('Car with vehicle registration number "'+str(regno)+'" has been parked at slot number '+ str(slotno))
                output.write('Car with vehicle registration number "'+str(regno)+'" has been parked at slot number '+ str(slotno)+"\n")

        # Exit of Vehicle
        elif line.startswith('Leave'):
            slotId = int(line.split(' ')[1])
            vacated = self.leave(slotId)
            if vacated != ErrorCode.NOTEXIST:
                print('Slot number '+str(slotId)+' vacated, the car with vehicle registration number "'+str(vacated.vehicle.regno)+'" left the space, the driver of the car was of age '+str(vacated.vehicle.driver.age))
                output.write('Slot number '+str(slotId)+' is free vacated, the car with vehicle registration number "'+str(vacated.vehicle.regno)+'" left the space, the driver of the car was of age '+str(vacated.vehicle.driver.age)+"\n")
            else:
                print("Slot number "+str(slotId)+" is already vacated, no vehicle has been parked at this slot")
                output.write("Slot number " +str(slotId)+" is already vacated, no vehicle has been parked at this slot\n")

        # Get slot with given reg no.
        elif line.startswith('Slot_number_for_car_with_number'):
            regno = line.split(' ')[1]
            slotno = self.getSlotNoFromRegNo(regno)
            if slotno == ErrorCode.NOTEXIST:
                print("Slot_number_for_car_with_number : Not found")
                output.write("Slot_number_for_car_with_number : " + str(regno)+" Not found\n")
            else:
                print("Slot_number_for_car_with_number : " + str(regno) + " is " + str(slotno))
                output.write("Slot_number_for_car_with_number : " + str(regno) + " is " + str(slotno)+"\n")

        # Get slots with given driver's age
        elif line.startswith('Slot_numbers_for_driver_of_age'):
            driver_age = line.split(' ')[1]
            slot_nos = self.getSlotNosFromAge(driver_age)
            if slot_nos != ErrorCode.NOTEXIST:
                print('Slot_numbers_for_driver_of_age '+str(driver_age)+" are " + str(slot_nos))
                output.write('Slot_numbers_for_driver_of_age '+str(driver_age)+" are " + str(slot_nos)+"\n")
            else:
                print ("No Driver with age " +str(driver_age))
                output.write("No Drivers with age " + str(driver_age)+"\n")

        # Get registration number with given driver's ags
        elif line.startswith('Vehicle_registration_number_for_driver_of_age'):
            driver_age = line.split(' ')[1]
            reg_nos = self.getVehicleRegNosFromAge(driver_age)
            if reg_nos != ErrorCode.NOTEXIST:
                print('Vehicle_registration_number_for_driver_of_age ' + str(driver_age) + " are " + str(reg_nos))
                output.write('Vehicle_registration_number_for_driver_of_age ' + str(driver_age) + " are " + str(reg_nos)+"\n")
            else:
                print("No Driver with age " + str(driver_age))
                output.write("No Drivers with age " + str(driver_age)+"\n")



def main():
    parkinglot = ParkingLot()
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', action="store", required=False, dest='src_file', help="Input File")
    args = parser.parse_args()
    output = open("output.txt", "w+")
    if args.src_file:
        with open(args.src_file) as f:
            for line in f:
                line = line.rstrip('\n')
                parkinglot.executeInstructions(line,output)
    else:
        while True:
            line = input("$ ")
            parkinglot.executeInstructions(line,output)

if __name__ == '__main__':
    main()




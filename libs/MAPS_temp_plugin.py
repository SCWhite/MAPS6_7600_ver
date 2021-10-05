# -*- coding: UTF-8 -*-
# mod for temp/RH plugin

import math
import time
import serial
import threading
from datetime import datetime
from collections import deque
from statistics import median

MIC_COM_PORT = '/dev/ttyACM0'
BAUD_RATES = 115200

#pairs = datetime.now().strftime("%Y-%m-%d %H-%M").split(" ")

#time_slot_string = ""
#slot_count = 0
#slot_energy = 0
#Leq = 0
#Leq_Max = 0
#Leq_Min = 0
#Leq_Median = 0

temp_data = 0
rh_data = 0

#notice: we use a sliding windows to calculate Max/Min/Mid
# one goes in, one come out
#dba_windows = deque(maxlen=60)


"""
# explan how Leq worked

 - first we have a lot of data in 1 second
    ex: dB(A)_t0 = 50 db ~ dB(A)_tn = 60 db

 - second, do  "pow(10,(x/5))" to get energy of t0

 - next, "sum up pow_t0 ~ pow_tn" and cacluate "pow_AVG" (depends on how long we want)

 - do a "sqrt(pow_AVG)" to get energy of this time period

 - last, caculate  "log10(energy_of__t0~tn) * 10" to get Leq of this time period (dB(A))

"""

"""
def transfer_to_eng(x):
    Lf = math.pow(10,(x/5))
    return Lf
"""

def get_temp_data():

    #global slot_count, slot_energy, Leq, time_slot_string
    #global Leq_Max, Leq_Min, Leq_Median, dba_windows
    global temp_data,rh_data

    while True:
        #ser = serial.Serial(MIC_COM_PORT, BAUD_RATES)
        try:
            ser = serial.Serial(MIC_COM_PORT, BAUD_RATES)

            #last_time_stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S").split(" ")[1]

            while True:
                #time_stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S").split(" ")[1]

                #if(time_stamp == last_time_stamp):
                if(1):
                    while ser.in_waiting:

                        data_raw = ser.readline()
                        data = data_raw.decode()

                        #input data: Temp:24.57,Humidity:51.82
                        data_set = data.strip().split(",")

                        #caculate dba to energy
                        #slot_energy =  slot_energy + transfer_to_eng(float(data_set[1]))
                        temp_data = float(data_set[0].split(":")[1])
                        rh_data = float(data_set[1].split(":")[1])

                        #print("------------------")
                        #print(temp_data)
                        #print(rh_data)
                        #print("------------------")

                        #time_slot_string = time_slot_string + str(data_set[1]) + ","
                        #slot_count = slot_count + 1

                #else:
                    #transfer back to dba / Leq in 1 seconds
                    #Leq = math.log10(math.sqrt(slot_energy / slot_count)) * 10
                    #limited to 2 places
                    #Leq = round(Leq,2)
                    #dba_windows.append(Leq)

                    #Leq_Max = max(dba_windows)
                    #Leq_Min = min(dba_windows)
                    #Leq_Median = round(median(dba_windows),2)
                    #print("Leq: " + str(Leq) + "\n")
                    #print("------------------")
                    #print("Leq: " + str(Leq) + "\n")
                    #print("Leq_Max: " + str(Leq_Max) + "\n")
                    #print("Leq_Min: " + str(Leq_Min) + "\n")
                    #print("Leq_Median: " + str(Leq_Median) + "\n")
                    #print("------------------")

                    #time_slot_string = ""
                    #slot_energy = 0
                    #slot_count = 0
                        #temp_data = 0
                        #rh_data = 0
                        #last_time_stamp = time_stamp

        except:
            ser.close()

            #clear remain data
            #dba_windows.clear()
            #Leq = 0
            #Leq_Max = 0
            #Leq_Min = 0
            #Leq_Median = 0
            temp_data = 0
            rh_data = 0

            time.sleep(5)
            #print('no MIC or port error!\n')
            #traceback.print_exc()


#start MIC sensing
get_temp_data_t = threading.Thread(target = get_temp_data)
get_temp_data_t.setDaemon(True)
get_temp_data_t.start()

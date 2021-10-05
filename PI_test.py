import os
import serial
import time
import libs.MAPS_mcu as mcu
import libs.MAPS_pi as pi
import libs.MAPS_temp_plugin as plugin
import libs.display as oled
from datetime import datetime

import requests
import threading

import traceback

#import current file's config, by getting the script name with '.py' replace by '_confg'
#ex: import "maps_V6_general.py" > "maps_V6_general_config" as Conf
PATH_OF_CONFIG = str(os.path.basename(__file__)[:-3] + "_config")
Conf = __import__(PATH_OF_CONFIG)

#temperary value
do_condition          = 1
sim7600_moudule       = 1
loop                  = 0
stop_query_sensor     = 0
initialize_flag       = 0
sim7600_fail_flag     = 0

#preset
TEMP            = 0
HUM             = 0
CO2             = 0
TVOC            = 0
Illuminance     = 0
PM1_AE          = 0
PM25_AE         = 0
PM10_AE         = 0
connection_flag = ""
#for dB sensor
#Leq         = 0
#Leq_Max     = 0
#Leq_Min     = 0
#Leq_Median  = 0
#for temp/RH plugin
temp_data = 0
rh_data   = 0
#location data
gps_lat = ""
gps_lon = ""

#open debug mode
#mcu.debug = 1

def show_task():
    while True:
        oled.display(Conf.DEVICE_ID,TEMP,HUM,PM25_AE,CO2,TVOC,connection_flag,Conf.ver_app)
        time.sleep(Conf.show_interval) #0.3 seconds / use about 18% cpu on PI3

def upload_task():
    while True:
        time.sleep(Conf.upload_interval) #300 seconds
        pairs = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S").split(" ")

        msg = ""

        if((gps_lat != "") and (gps_lon != "")):
            msg = msg + "|gps_lon="+ gps_lon + "|gps_lat=" + gps_lat
        if(CO2 != 65535):
            msg = msg + "|s_g8=" + str(CO2)

        msg = msg + "|s_t0=" + str(TEMP) + "|app=" + str(Conf.APP_ID) + "|date=" + pairs[0] + "|s_d0=" + str(PM25_AE) + "|s_h0=" + str(HUM) + "|device_id=" + Conf.DEVICE_ID + "|s_gg=" + str(TVOC) + "|ver_app=" + str(Conf.ver_app) + "|time=" + pairs[1]

        #if(Leq != 0):
        #    msg = msg + "|s_s0=" + str(Leq_Median) + "|s_s0M=" + str(Leq_Max) + "|s_s0m=" + str(Leq_Min) + "|s_s0L=" + str(Leq)
        if(temp_data != 0):
            msg = msg + "|add_temp=" + str(temp_data) + "|add_RH=" + str(rh_data)


        print("message ready")
        restful_str = Conf.Restful_URL + "topic=" + Conf.APP_ID + "&device_id=" + Conf.DEVICE_ID + "&key=" + Conf.SecureKey + "&msg=" + msg
        try:
            r = requests.get(restful_str)
            print("send result")
            print(r)
            print("message sent!")
        except:
            print("internet err!!")
        #save after upload / makesure data will be synchronize
        #format_data_list = [Conf.DEVICE_ID,pairs[0],pairs[1],TEMP,HUM,PM25_AE,PM1_AE,PM10_AE,Illuminance,CO2,TVOC,Leq,Leq_Max,Leq_Min,Leq_Median,gps_lat,gps_lon]
        #mod for temp/RH plugin
        format_data_list = [Conf.DEVICE_ID,pairs[0],pairs[1],TEMP,HUM,PM25_AE,PM1_AE,PM10_AE,Illuminance,CO2,TVOC,temp_data,rh_data,gps_lat,gps_lon]
        try:
            pi.save_data(path,format_data_list) #save to host
            pi.save_to_SD(format_data_list)     #save to SD card
            print("send message saved!")
        except:
            print("Fail to save sent message!(upload)")
            traceback.print_exc()


def save_task():
    while True:
        time.sleep(Conf.save_interval) #60 seconds
        #format to ['device_id', 'date', 'time', 'Tmp',  'RH',   'PM2.5','PM10', 'PM1.0','Lux',  'CO2',  'TVOC' ,'Leq','Leq_Max','Leq_Min','Leq_Median','gps_lat','gps_lon']
        pairs = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S").split(" ")
        #format_data_list = [Conf.DEVICE_ID,pairs[0],pairs[1],TEMP,HUM,PM25_AE,PM1_AE,PM10_AE,Illuminance,CO2,TVOC,Leq,Leq_Max,Leq_Min,Leq_Median,gps_lat,gps_lon]
        #mod for temp/RH plugin
        format_data_list = [Conf.DEVICE_ID,pairs[0],pairs[1],TEMP,HUM,PM25_AE,PM1_AE,PM10_AE,Illuminance,CO2,TVOC,temp_data,rh_data,gps_lat,gps_lon]
        #print("********")
        #print(format_data_list)
        #print("********")
        try:
            pi.save_data(path,format_data_list) #save to host
            pi.save_to_SD(format_data_list)     #save to SD card
            print("message saved!")
        except:
            print("Fail to save message!(regular save)")


def sim7600_sending_task():
    global initialize_flag
    global sim7600_fail_flag
    global stop_query_sensor
    global sim7600_moudule
    global gps_lat,gps_lon

    while(initialize_flag != 1):
        time.sleep(5)

    print("sim7600_sending_task start!!!")
    mcu.PROTOCOL_UART_BEGIN(0,4) #use port:0 / set to '4' as 115200 baud


    while (sim7600_moudule):
        try:
            time.sleep(Conf.sim7600_send_interval * 0.4) #60 seconds/ but in seperate part / to shift away form upload
            stop_query_sensor = 1  #halt getting sensor data for a while

            #pairs = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S").split(" ")

            #msg = ""
            #message_package_part = []

            #if((gps_lat != "") and (gps_lon != "")):
            #    msg = msg + "|gps_lon="+ gps_lon + "|gps_lat=" + gps_lat
            #if(CO2 != 65535):
            #    msg = msg + "|s_g8=" + str(CO2)

            #msg = msg + "|s_t0=" + str(TEMP) + "|app=" + str(Conf.APP_ID) + "|date=" + pairs[0] + "|s_d0=" + str(PM25_AE) + "|s_h0=" + str(HUM) + "|device_id=" + Conf.DEVICE_ID + "|s_gg=" + str(TVOC) + "|ver_app=" + str(Conf.ver_app) + "|time=" + pairs[1] + "|s_s0=" + str(Leq_Median) + "|s_s0M=" + str(Leq_Max) + "|s_s0m=" + str(Leq_Min) + "|s_s0L=" + str(Leq)

            #print("------------------------")
            #print("msg_for_sim7600:",msg)
            print("=============================================")

            #clear input buffer
            #while(ser.inWaiting()!=0):
            #    data = mcu.ser.readline()
            mcu.ser.reset_input_buffer()

            at_cmd = "AT\r"
            check_cmd =  mcu.PROTOCOL_UART_TXRX_EX(0,at_cmd.encode(),250,3000)

            if(check_cmd[1] == "empty"):
                print("NO moudle")
                sim7600_moudule = 0
                raise 'error'

            #print("----start GPS----")
            at_cmd = "AT+CGPS=1\r"
            mcu.PROTOCOL_UART_TXRX_EX(0,at_cmd.encode(),250,3000)

            #print("----get GPS data----")
            at_cmd = "AT+CGPSINFO\r"
            gps_info = mcu.PROTOCOL_UART_TXRX_EX(0,at_cmd.encode(),250,3000)

            gps_info_str = ""

            for i in range(len(gps_info[1])):
                gps_info_str = gps_info_str + chr(gps_info[1][i])


            gps_info_str = gps_info_str.replace("\n","").replace("\r","").replace("OK","")
            #print(gps_info_str)

            gps_info_str = gps_info_str.split(":")[1]
            #print(gps_info_str)

            #put dummy here
            #gps_info_str = "3113.343286,N,12121.234064,E,250311,072809.3,44.1,0.0,0"

            gps_info_str = gps_info_str.strip(" ")
            gps_info_str = gps_info_str.split(",")

            #check if it is empty here
            if((gps_info_str[0]!= "")and(gps_info_str[2]!="")):

                gps_lat   = gps_info_str[0]
                gps_lat_a = int(gps_lat[:2])
                gps_lat_b = float(gps_lat[2:])
                gps_lat   = round(gps_lat_a + (gps_lat_b/60),4)
                gps_lat   = str(gps_lat)

                gps_NS    = gps_info_str[1]

                gps_lon   = gps_info_str[2]
                gps_lon_a = int(gps_lon[:3])
                gps_lon_b = float(gps_lon[3:])
                gps_lon   = round(gps_lon_a + (gps_lon_b/60),4)
                gps_lon   = str(gps_lon)

                gps_EW    = gps_info_str[3]
                gps_date  = gps_info_str[4]
                gps_time  = gps_info_str[5]
                gps_alt   = gps_info_str[6]
                gps_speed = gps_info_str[7]
                gps_speed = round(float(gps_speed)*1.852,4)
            else:
                gps_lat = ""
                gps_lon = ""

            #print("-------!!---------")
            #print("gps_lat :" + gps_lat)
            #print("gps_lon :" + gps_lon)
            #print("-------!!---------")

            #print("----MQTT part----")
            at_cmd = "AT+CMQTTSTART\r"
            mcu.PROTOCOL_UART_TXRX_EX(0,at_cmd.encode(),250,3000)

            #print("----MQTT set client----")
            at_cmd = "AT+CMQTTACCQ=0,\"" + Conf.DEVICE_ID + "\"\r"
            mcu.PROTOCOL_UART_TXRX_EX(0,at_cmd.encode(),250,3000)

            #print("----MQTT set connection----")
            at_cmd = "AT+CMQTTCONNECT=0,\"tcp://35.162.236.171:8883\",20,1,\"maps\",\"iisnrl\"\r"
            mcu.PROTOCOL_UART_TXRX_EX(0,at_cmd.encode(),250,3000)
            time.sleep(3)

            #print("----MQTT set topic----")
            at_cmd = "AT+CMQTTTOPIC=0,23\r"
            mcu.PROTOCOL_UART_TXRX_EX(0,at_cmd.encode(),250,3000)

            at_cmd = "MAPS/MAPS6/" + Conf.DEVICE_ID + "\r"
            mcu.PROTOCOL_UART_TXRX_EX(0,at_cmd.encode(),250,3000)

            #set MQTT message
            pairs = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S").split(" ")

            msg = ""

            if((gps_lat != "") and (gps_lon != "")):
                msg = msg + "|gps_lon="+ gps_lon + "|gps_lat=" + gps_lat
            if(CO2 != 65535):
                msg = msg + "|s_g8=" + str(CO2)

            msg = msg + "|s_t0=" + str(TEMP) + "|app=" + str(Conf.APP_ID) + "|date=" + pairs[0] + "|s_d0=" + str(PM25_AE) + "|s_h0=" + str(HUM) + "|device_id=" + Conf.DEVICE_ID + "|s_gg=" + str(TVOC) + "|ver_app=" + str(Conf.ver_app) + "|time=" + pairs[1]

            #if(Leq != 0):
            #    msg = msg + "|s_s0=" + str(Leq_Median) + "|s_s0M=" + str(Leq_Max) + "|s_s0m=" + str(Leq_Min) + "|s_s0L=" + str(Leq)
            if(temp_data != 0):
                msg = msg + "|add_temp=" + str(temp_data) + "|add_RH=" + str(rh_data)

            msg = msg + "|MQ"

            payload_len = len(msg)

            #print("----MQTT set message----") #fix

            at_cmd = "AT+CMQTTPAYLOAD=0," + str(payload_len) + "\r"
            mcu.PROTOCOL_UART_TXRX_EX(0,at_cmd.encode(),250,3000)

            #add payload

            at_cmd = msg
            mcu.PROTOCOL_UART_TXRX_EX(0,at_cmd.encode(),250,3000)


            #print("----publish MQTT message----")
            at_cmd = "AT+CMQTTPUB=0,1,60\r"
            mcu.PROTOCOL_UART_TXRX_EX(0,at_cmd.encode(),250,3000)

            #print("----Disconnect from the server----")
            at_cmd = "AT+CMQTTDISC=0,60\r"
            mcu.PROTOCOL_UART_TXRX_EX(0,at_cmd.encode(),250,3000)
            time.sleep(1)

            #print("----MQTT release client----")
            at_cmd = "AT+CMQTTREL=0"
            mcu.PROTOCOL_UART_TXRX_EX(0,at_cmd.encode(),250,3000)
            time.sleep(1)

            #print("----stop MQTT----")
            at_cmd = "AT+CMQTTSTOP\r"
            mcu.PROTOCOL_UART_TXRX_EX(0,at_cmd.encode(),250,3000)

            #should add clean buffer here
            #mcu.ser.readline()
            #mcu.ser.readline()
            #mcu.ser.readline()
            mcu.ser.reset_input_buffer()

            stop_query_sensor = 0  #resume getting sensor data
            sim7600_fail_flag = 0  #sim7600 is good
            time.sleep(Conf.sim7600_send_interval * 0.6) #the rest of time interval

        except:
            print("=====sim7600 Fail====")
            traceback.print_exc()
            #should add clean buffer here
            #mcu.ser.readline()
            #mcu.ser.readline()
            #mcu.ser.readline()
            mcu.ser.reset_input_buffer()

            sim7600_fail_flag = 1
            stop_query_sensor = 0 #keep getting data

def connection_task():
    while True:
        time.sleep(10)
        check_connection()


def check_connection():
    global connection_flag
    if(os.system('ping www.google.com -q -c 1  > /dev/null')):
        connection_flag = "X"
        #print("no internet")
        #return 0

    else:
        connection_flag = "@"
        #print("connect OK")
        #return 1

def get_rtc_server_time():
    try:
        command = "wget -O /tmp/time1 " + Conf.TimeURL + " >/dev/null 2>&1"
        os.system(command)
        fh = open("/tmp/time1","r")
        server_time = fh.read()
        server_time = datetime.strptime(server_time, "%Y-%m-%d %H:%M:%S")
        print("got sever time:" + str(server_time))
        return 1 , server_time
    except:
        host_time = datetime.utcnow()
        print("use host time:" + str(host_time))
        return 0 , host_time  #no internet, use system time


#start oled displaying
display_t = threading.Thread(target = show_task, name = "display_t")
display_t.setDaemon(True)

#start upload routine
upload_t = threading.Thread(target = upload_task, name = "upload_t")
upload_t.setDaemon(True)

#start save routine
save_t = threading.Thread(target = save_task, name = "save_t")
save_t.setDaemon(True)

#start connection routine
connection_t = threading.Thread(target = connection_task, name = "connection_t")
connection_t.setDaemon(True)

#sim7600 routine
sim7600_sending_t = threading.Thread(target = sim7600_sending_task, name = "sim7600_sending_t")
sim7600_sending_t.setDaemon(True)


try:
    print("START")
    print("========================")

    print("open port & init mcu")
    mcu.ser=serial.Serial("/dev/ttyS0",115200,timeout=1) #for PI (not ttyAMA0)(use /dev/ttyS0)
    time.sleep(5)
    print("mcu ok\n")
    print("========================")
    print("CHECK INTERNET")
    # if(check_connection()):

    #     print("-----with internet------")
    #     print("CHECK TIME")
    #     current_mcu_time = mcu.GET_RTC_DATE_TIME()
    #     print("MCU RTC time:")
    #     print(current_mcu_time)

    #     time_status, server_time =  get_rtc_server_time()
    #     if(time_status):
    #         host_time = datetime.utcnow()
    #         delta_time = host_time - server_time
    #         print("delta_time:" + str(delta_time))

    #         if abs(delta_time.seconds) > 30:
    #             print("!!!SET TO severtime!!!")
    #             print("server time:")
    #             print(server_time)
    #             print("host time")
    #             print(host_time)
    #             #to do
    #             #set system time
    #             #set mcu RTC time
    #         else:
    #             print("!!!use host time is ok!!!")
    #             print("server time:")
    #             print(server_time)
    #             print("host time")
    #             print(host_time)
    #             #to do
    #             #set mcu RTC time


    # else:
    #     print("-----no internet------")
    #     print("-----pass time check------")
    #     current_mcu_time = mcu.GET_RTC_DATE_TIME()
    #     print("MCU RTC time:")
    #     print(current_mcu_time)
    #     #set system time to mcu RTC clock time

    print("------------------------")
    print("CHECK PI VERSION")

    print("CHECK MCU VERSION")

    current_mcu_version = mcu.GET_INFO_VERSION()
    print(current_mcu_version)
    #if (current_mcu_version < Conf.latest_mcu_version):
    #    #need update
    #    print("please update mcu")
    #else:
    #    print("newest version")
    print("------------------------")
    print("SET SENSOR")

    mcu.SET_POLLING_SENSOR(Conf.POLL_TEMP,Conf.POLL_CO2,Conf.POLL_TVOC,Conf.POLL_LIGHT,Conf.POLL_PMS,Conf.POLL_RTC)

    print("CHECK SENSOR")
    print(mcu.GET_INFO_SENSOR_POR())


    print("------------------------")
    print("CHECK STORAGE")
    #In MPV version, only use "./data"
    path = pi.GET_STORAGE_PATH()
    print(path)

    print("CHECK read/write")
    #TODO

    print("------------------------")
    print("set upload")
    #if need to do
    print("------------------------")
    print("CHECK SIM7600")
    #do it in another part

    #set pin status for sim7600
    mcu.SET_PIN_NBIOT_PWRKEY(0)
    mcu.SET_PIN_NBIOT_SLEEP(0)

    print("CHECK GPS")
    #check if there is GPS module
    #and if we want to use GPS, set "use_GPS" to 1

    print("------------------------")

    #start routine job
    display_t.start()
    upload_t.start()
    save_t.start()
    connection_t.start()
    sim7600_sending_t.start()

    #mcu initialize over
    initialize_flag = 1


    while (do_condition):
        print("START GET DATA (loop:" + str(loop) + ")")
        print("========================")

        if(stop_query_sensor == 0):
            print("check thread alive")
            print("display_t: "        + str(display_t.is_alive()))
            print("upload_t: "         + str(upload_t.is_alive()))
            print("save_t: "           + str(save_t.is_alive()))
            print("connection_t: "     + str(connection_t.is_alive()))
            print("sim7600_sending_t: "  + str(sim7600_sending_t.is_alive()))
            print("------------------------")

        if(stop_query_sensor == 0):
            print("GET ALL DATA")
            data_list = mcu.GET_SENSOR_ALL()
        else:
            print("==data on pause==")

        TEMP        = data_list[0]
        HUM         = data_list[1]
        CO2         = data_list[2]
        TVOC        = data_list[4]
        Illuminance = data_list[10]
        PM1_AE      = data_list[16]
        PM25_AE     = data_list[17]
        PM10_AE     = data_list[18]


        #for dB sensor
        #Leq         = plugin.Leq
        #Leq_Max     = plugin.Leq_Max
        #Leq_Min     = plugin.Leq_Min
        #Leq_Median  = plugin.Leq_Median
        #

        #for temp/RH plugin
        temp_data = plugin.temp_data
        rh_data   = plugin.rh_data
        #

        if(stop_query_sensor == 0):
            print("TEMP:"         + str(TEMP))
            print("HUM:"          + str(HUM))
            print("CO2:"          + str(CO2))
            print("TVOC:"         + str(TVOC))
            print("Illuminance:"  + str(Illuminance))
            print("PM1_AE:"       + str(PM1_AE))
            print("PM25_AE:"      + str(PM25_AE))
            print("PM10_AE:"      + str(PM10_AE))
            #print("Leq:"          + str(Leq))
            #print("Leq_Max:"      + str(Leq_Max))
            #print("Leq_Min:"      + str(Leq_Min))
            #print("Leq_Median:"   + str(Leq_Median))
            print("add_on_temp:"  + str(temp_data))
            print("add_on_RH:"    + str(rh_data))
            print("------------------------")

        loop = loop + 1

        #prevent overload
        if(loop > 10000):
            loop = 0

        time.sleep(5)
        print("========================")

except KeyboardInterrupt:
    mcu.ser.close()
    print("ERROR!!")
    pass



mcu.ser.close()

print("exit OK")

import os

#for nbiot
#def formatStrToInt(target):
#    kit = ""
#    for i in range(len(target)):
#        temp=ord(target[i])
#        temp=hex(temp)[2:]
#        kit=kit+str(temp)+" "
#        #print(temp,)
#    return kit

#ID
DEVICE_ID = "MAPSV6_001"

#IP
DEVICE_IP = ""

#APP ID
APP_ID = "MAPS6"

#GPS
gps_lat = ""
gps_lon = ""

#key
SecureKey = "NoKey"

#mcu version
latest_mcu_version = 1000
ver_app            = "6.5.0-b"  # 6.x.x-b for NTU project (with SIM7600 support) / 6.5.0-b add PQC


#path
FS_SD = "./data"

# #If there is no "data" folder in path
# if not os.path.isdir(FS_SD):
#     os.mkdir(FS_SD)


#Enable 1:on / 0:off
POLL_TEMP  = 1
POLL_CO2   = 1
POLL_TVOC  = 1
POLL_LIGHT = 1
POLL_PMS   = 1
POLL_RTC   = 1

#url
Restful_URL = "https://data.lass-net.org/Upload/MAPS-secure.php?"
TimeURL = "https://pm25.lass-net.org/util/timestamp.php"

#setting
#GPS_LAT = ""
#GPS_LON = ""


mac = open('/sys/class/net/eth0/address').readline().upper().strip()
DEVICE_ID = mac.replace(':','')


#interval(in seconds)
show_interval         = 0.3
upload_interval       = 60
save_interval         = 1
sim7600_send_interval = 60

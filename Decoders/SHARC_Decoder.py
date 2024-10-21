import csv
import binascii
import struct
import DecoderFunctions
import uuid
from datetime import datetime
import json
import shutil
import os
import sys
# Date Time (UTC),Device,Direction,Payload,Approx Lat/Lng,Payload (Text),Length (Bytes),Credits


def extract_with_offset(payload,offset,start):
    out_hex = payload[start + offset:start +8 + offset]
    out_hex = out_hex[6:8]+out_hex[4:6]+out_hex[2:4]+out_hex[0:2]
    out_int = int(out_hex, 16)
    out = struct.unpack('<f', struct.pack('<I', out_int))[0]
    return out

def payload_decode(payload,offset,oldfirmware = False):
    lat_start = 10
    lon_start = 18
    if oldfirmware:
        lat_start = 18
        lon_start = 26
    lat = extract_with_offset(payload,offset,lat_start)
    lon = extract_with_offset(payload,offset,lon_start)
    return lat,lon

def deg_to_DMS(deg):
    deg = float(deg)
    degrees = int(deg)
    temp = 60 * (deg - degrees)
    minutes = int(temp)
    seconds = 60 * (temp - minutes)
    return degrees,minutes,seconds


def filetodict(filename):
    output = {}
    with open(filename, mode='r') as file:
        csv_reader = csv.DictReader(file)
        line_count = 0
        for row in csv_reader:
            # Ignore first line
            if line_count == 0:
                line_count += 1
                continue
            
            # Extract information
            datetime = row['Date Time (UTC)']
            devicename = row['Device']
            payload = row['Payload']
            [iridium_lat,iridium_lon] = row['Approx Lat/Lng'].split(',')
            ir_lat_d,ir_lat_m,ir_lat_s = deg_to_DMS(iridium_lat)
            ir_lon_d,ir_lon_m,ir_lon_s = deg_to_DMS(iridium_lon)

            # Decode and    
            try:
                offset = 2 * (28 + 32 + 1)
                if ("SB04" in devicename or "SB06" in devicename):
                    lat,lon = payload_decode(payload,offset, True)
                else:
                    lat,lon = payload_decode(payload,offset)
                lat_d,lat_m,lat_s = deg_to_DMS(lat)
                lon_d,lon_m,lon_s = deg_to_DMS(lon)

                row_data = [
                    datetime,
                    devicename,
                    lat,
                    lat_d,
                    lat_m,
                    lat_s,
                    lon,
                    lon_d,
                    lon_m,
                    lon_s,
                    iridium_lat,
                    ir_lat_d,
                    ir_lat_m,
                    ir_lat_s,
                    iridium_lon,
                    ir_lon_d,
                    ir_lon_m,
                    ir_lon_s,
                ]

                # Add this row's data to the output dictionary, using devicename as the key
                if devicename not in output:
                    output[devicename] = []
                output[devicename].append(row_data)
            
            except:
                print("There was an error extracting a row")
            
            line_count += 1

    return output



def writetofile(data):
    headings = ["UTC Time","Device Name","GPS Latitude","GPS Latitude DMS_1","GPS Latitude DMS_2","GPS Latitude DMS_3","GPS Longitude","GPS Longitude DMS_1","GPS Longitude DMS_2","GPS Longitude DMS_3",
    "Iridium Approx Latitude","Iridium Approx Latitude DMS_1","Iridium Approx Latitude DMS_2","Iridium Approx Latitude DMS_3","Iridium Approx Longitude","Iridium Approx Longitude DMS_1","Iridium Approx Longitude DMS_2","Iridium Approx Longitude DMS_3"]
    for device in list(data.keys()):
        writer = csv.writer(open("Decoders/Outputs/"+device+'.csv', mode='w',newline=""), delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(headings)
        for row in data[device]:
            try:
                writer.writerow(row)
            except:
                continue
        



def writetodatabase(data,userid,status):
    # Get Data Necessary For Checking Things
    users = DecoderFunctions.getusers(userid)
    datasources = DecoderFunctions.getdatasources()

    # If user doesnt exists return
    if len(users) != 1:
        return
    #print("Here")
    #print(data)
    # Iterate over devices
    for device in list(data.keys()):
        device_exists = False
        owned = False
        print("Working on:",device)
        # Check if device exists
        for datasource in datasources:
            if datasource["Name"] == device:
                device_exists = True

        # If the device exists check if the user owns it
        if device_exists:
            for datasource in users[0]["DataSources"]:
                if datasource["Name"] == device:
                    datasourceuuid = datasource["UUID"]
                    owned = True
        # If the device doesnt exist we must create it
        if not device_exists:
            datasourceuuid = str(uuid.uuid1())
            #print('Creating new datasource:',datasource)
            DecoderFunctions.add_new_datasource(datasourceuuid, device)
            DecoderFunctions.add_datasource_to_user(userid,datasourceuuid)
            #print("Create device")
            owned = True
            device_exists = True

        # Only if the device exists and the user owns it do we add data
        if device_exists and owned:
            print("Adding Dataset")
            datasetuuid = str(uuid.uuid1())
            DecoderFunctions.add_new_dataset(datasetuuid,device)
            DecoderFunctions.add_dataset_to_datasource(datasetuuid,datasourceuuid)
            #DecoderFunctions.add_dataset_to_user(userid,datasetuuid)
            print("Adding Dataset File")
            DecoderFunctions.add_file_to_dataset(datasetuuid,device+".csv")
            print("Adding Datasource Locations")
            for location in data[device]:
                #print(location)
                temploc = str(location[2])+","+str(location[6])
                parsed_date = datetime.strptime(location[0], "%d/%b/%Y %H:%M:%S")
                DecoderFunctions.add_location_to_datasource(datasourceuuid,temploc,parsed_date,"",status)
                #print(location[0],location[2],location[6])

            # Move files to correct place
            dataset_path = os.path.join("uploads", 'Datasets', datasetuuid)
            if not os.path.exists(dataset_path):
                os.makedirs(dataset_path)
            shutil.move("Decoders/Outputs/"+device+".csv", dataset_path)

            

    
            
def optionsreader(filename):
    if filename == 'None':
        filename = "Decoders/SHARC_Decoder_Default.json"
    with open(filename, 'r') as f:
        data = json.load(f)
    return data


def main(filename,optsfilename,userid):
    outputs = filetodict(filename)
    status = optionsreader(optsfilename)["status"]
    #print(outputs[list(outputs.keys())[0]])
    writetofile(outputs)
    writetodatabase(outputs,userid,status)



    # write to database
    #print(outputs)
args = sys.argv[1:]
#print(args[0],args[1],args[2])
#main('Decoders/SB All.csv',"Decoders/sharc_opts.txt","30375628-ed13-4fd5-8e58-21dfbc04a0af")
main(args[0],args[1],args[2])
import csv
import binascii
import struct
import uuid
from datetime import datetime
import json
import shutil
import os
import sys
# Date Time (UTC),Device,Direction,Payload,Approx Lat/Lng,Payload (Text),Length (Bytes),Credits

        

            
def optionsreader(filename):
    if filename == 'None':
        filename = "Encoders/SHARC_Encoder_Default.json"
    with open(filename, 'r') as f:
        data = json.load(f)
    return data

def readcommandfile(filename):
    with open(filename, 'r') as f:
        data = json.load(f)
    return data


def main(filename,optsfilename,userid):
    optionsfile = optionsreader(optsfilename)
    commandfilecontents = readcommandfile(filename)
    if commandfilecontents["command"] == "Ping":
        print("Device Replied: Pong")
    if commandfilecontents["command"] == "GetData":
        print("1.573,19.189,2.981,22.190")
    if commandfilecontents["command"] == "GetBattery":
        print("5.5 v")




    # write to database
    #print(outputs)
args = sys.argv[1:]
#print(args[0],args[1],args[2])
#main('Decoders/SB All.csv',"Encoders/sharc_opts.txt","30375628-ed13-4fd5-8e58-21dfbc04a0af")
main(args[0],args[1],args[2])
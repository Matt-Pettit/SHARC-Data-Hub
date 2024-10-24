import csv
import uuid
from datetime import datetime
import json
import shutil
import os
import sys
import DecoderFunctions

def process_csv(filename, options):
    output = {}
    
    with open(filename, mode='r') as file:
        csv_reader = csv.DictReader(file)
        
        for row in csv_reader:
            try:
                # Get device name (either from config or CSV)
                devicename = options.get('device_name') or row.get(options.get('device_column', ''))
                if not devicename:
                    print("No device name found in config or CSV")
                    continue

                # Get datetime if specified
                datetime_str = None
                parsed_datetime = None
                if 'datetime_column' in options and 'datetime_format' in options:
                    datetime_str = row[options['datetime_column']]
                    parsed_datetime = datetime.strptime(datetime_str, options['datetime_format'])

                # Get coordinates if specified
                location = None
                if 'latitude_column' in options and 'longitude_column' in options:
                    try:
                        lat = float(row[options['latitude_column']])
                        lon = float(row[options['longitude_column']])
                        location = f"{lat},{lon}"
                    except (ValueError, KeyError):
                        # If coordinates can't be parsed, continue without location data
                        pass

                if devicename not in output:
                    output[devicename] = {
                        'locations': [],
                        'has_coordinates': bool(location),
                        'filename': os.path.basename(filename)
                    }

                if location and parsed_datetime:
                    output[devicename]['locations'].append((location, parsed_datetime))

            except Exception as e:
                print(f"Error processing row: {str(e)}")
                continue

    return output

def writetodatabase(data, userid, status):
    users = DecoderFunctions.getusers(userid)
    datasources = DecoderFunctions.getdatasources()

    if len(users) != 1:
        print(f"User {userid} not found or multiple users found")
        return

    for device in data:
        device_exists = False
        owned = False
        print(f"Processing device: {device}")

        # Check if device exists and is owned
        for datasource in datasources:
            if datasource["Name"] == device:
                device_exists = True
                for user_datasource in users[0]["DataSources"]:
                    if user_datasource["Name"] == device:
                        datasourceuuid = user_datasource["UUID"]
                        owned = True
                        break

        # Create new device if it doesn't exist
        if not device_exists:
            datasourceuuid = str(uuid.uuid1())
            DecoderFunctions.add_new_datasource(datasourceuuid, device)
            DecoderFunctions.add_datasource_to_user(userid, datasourceuuid)
            owned = True

        if owned:
            # Create new dataset
            datasetuuid = str(uuid.uuid1())
            DecoderFunctions.add_new_dataset(datasetuuid, device)
            DecoderFunctions.add_dataset_to_datasource(datasetuuid, datasourceuuid)
            
            # Create dataset directory and copy file
            dataset_path = os.path.join("uploads", 'Datasets', datasetuuid)
            os.makedirs(dataset_path, exist_ok=True)
            
            original_filename = data[device]['filename']
            shutil.copy2(original_filename, os.path.join(dataset_path, original_filename))
            DecoderFunctions.add_file_to_dataset(datasetuuid, original_filename)

            # Add location data if available
            if data[device]['has_coordinates']:
                for location, datetime_val in data[device]['locations']:
                    DecoderFunctions.add_location_to_datasource(
                        datasourceuuid, location, datetime_val, "", status
                    )

def optionsreader(filename):
    if filename == 'None':
        filename = "Decoders/Generic_Decoder_Default.json"
    with open(filename, 'r') as f:
        data = json.load(f)
    return data

def main(filename, optsfilename, userid):
    try:
        # Load options
        options = optionsreader(optsfilename)
        
        # Process CSV and handle database operations
        data = process_csv(filename, options)
        writetodatabase(data, userid, options.get("status", "active"))
        
        print("Processing completed successfully")
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    args = sys.argv[1:]
    main(args[0], args[1], args[2])

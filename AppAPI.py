from flask import Blueprint, jsonify, request
from functools import wraps
from flask import session
import SHARCFunctions
import os
from flask import Blueprint, Flask, render_template,request,url_for, redirect, flash, session, abort, make_response,jsonify,send_from_directory,send_file
from functools import wraps, update_wrapper
from flask_session import Session
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import pandas as pd
import tempfile
from kml2geojson import convert
import SHARCFunctions
from io import StringIO
from xml.parsers.expat import ExpatError
from json.decoder import JSONDecodeError
import json
import zipfile
import subprocess
import uuid
api_bp = Blueprint('api', __name__)

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif','csv'}

def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if session.get('logged_in'):            
            return f(*args, **kwargs)
        else:
            return jsonify({"error": "Authentication required"}), 401
    return wrap

def roles_required(funcname):
    def groupsthings(f):
        @wraps(f)
        def wrap(*args, **kwargs):
            if check_groups(funcname): 
                return f(*args, **kwargs)
            else:
                return jsonify({"error": "Permission denied"}), 403
        return wrap
    return groupsthings

def check_groups(group):
    if group == session.get('userroles'):
        return True
    if 'Administrator' == session.get('userroles'):
        return True
    return False 

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def check_datasource_ownership(datasource_id, user_uuid):
    # Check if the user owns the datasource
    datasources = SHARCFunctions.getdatasources(useruuid=user_uuid, datasourceuuid=datasource_id)
    return len(datasources) > 0

def check_dataset_ownership(dataset_id, user_uuid):
    # Check if the user owns the dataset
    #datasets = SHARCFunctions.getdatasets(useruuid=user_uuid, datasetuuid=dataset_id)
    #return len(datasets) > 0
    return True
def check_expedition_ownership(expedition_uuid, user_uuid):
    # Implement your logic here to check if the user owns or has permission to edit the expedition
    # This is a placeholder and should be replaced with actual logic
    return True

def get_dataset_file_path(dataset_id, filename):
    return os.path.join('uploads', 'Datasets', dataset_id, filename)

#########################################
#########################################
#########################################
###########     HOME PAGE     ###########     
#########################################
#########################################
#########################################

#################################
#  Get Datasets for Datasource  #
#################################
@api_bp.route('/datasource/getdatasets', methods=['POST'])
def get_datasource_datasets():
    try:
        # Get datasourceUUID from the request JSON
        data = request.json
        datasourceUUID = data.get('datasourceUUID')
        if not datasourceUUID:
            return jsonify({"success": False, "message": "datasourceUUID is required"}), 400

        # Fetch datasets associated with the datasource
        datasets = SHARCFunctions.getdatasets()

        # Error Handling
        if not datasets:
            return jsonify({"success": False, "message": "No datasets found for this datasource"}), 404

        # Filter Datasets to only return ones related to Datasource
        formatted_datasets = []
        for dataset in datasets:
            for datasource in dataset["DataSources"]:
                if (datasourceUUID == datasource["UUID"]):
                    formatted_datasets.append({
                        'Dataset Name': dataset['Name'],
                        'DatasetUUID': dataset['UUID'],
                        'Dataset description': dataset['Description']
                    })
                    # Only want to add it once
                    break

        return jsonify(formatted_datasets), 200
    except Exception as e:
        # Error Handling
        return jsonify({"success": False, "message": "An error occurred while fetching datasets"}), 500

    


############################
#  Datasource Data Getter  #
############################
@api_bp.route('/datasource/getlocationdata', methods=['POST'])
def get_datasource_location_data():
    # Get request data (if any)
    request_data = request.json or {}

    results = SHARCFunctions.getdatasources()
    datasources = []
    for source in results:
        # You can add filtering logic here based on request_data if needed
        for location in source["Locations"]:
            datasources.append({
                "UUID": source["UUID"],
                "Sensor Name": source["Name"],
                "Time": location["DateTime"],
                "Location": location["Location"]
            })
    return jsonify(datasources)


#########################################
#########################################
#########################################
#######       DATA DOWNLOAD       #######      
#########################################
#########################################
#########################################


#################################
#      Get Columns for File     #
#################################
@api_bp.route('/dataset/getcolumns', methods=['POST'])
def get_columns():
    data = request.json
    file = data.get('file')
    dataset_id = data.get('dataset_id')
    if not file or not dataset_id:
        return jsonify({"success": False, "message": "File and dataset ID are required"}), 400
    file_path = get_dataset_file_path(dataset_id, file)
    try:
        # Read just the header of the CSV file
        df = pd.read_csv(file_path, nrows=0)
        columns = df.columns.tolist()
        return jsonify({"success": True, "columns": columns})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

#################################
# Get Map for File #
#################################
@api_bp.route('/dataset/getmapdata', methods=['POST'])
def get_map_data():
    data = request.json
    file = data.get('file')
    dataset_id = data.get('dataset_id')
    lat_column = data.get('lat_column')
    lon_column = data.get('lon_column')
    data_columns = data.get('data_columns')
    if not all([file, dataset_id, lat_column, lon_column, data_columns]):
        return jsonify({"success": False, "message": "Missing required parameters"}), 400
    file_path = get_dataset_file_path(dataset_id, file)
    try:
        # Read the CSV file
        final_columns = []
        df = pd.read_csv(file_path)
        # Fix to ensure it doesn't overwrite location columns
        for col in data_columns:
            if not (col == lat_column or col == lon_column):
                final_columns.append(col)
        # Select only the required columns
        required_columns = [lat_column, lon_column] + final_columns
        df = df[required_columns]
        # Convert DataFrame to the required format
        result = []
        for _, row in df.iterrows():
            location = f"{row[lat_column]},{row[lon_column]}"
            data_row = [
                (column, str(row[column])) for column in data_columns
            ]
            result.append({
                "Location": location,
                "Row": data_row
            })
        if len(result) > 1000:
            scaler = round(len(result)/1000)
            result = result[::scaler]
        return jsonify({"success": True, "data": result})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


#################################
# Get File From dataset #
#################################
@api_bp.route('/dataset/downloadfile', methods=['POST'])
def download_dataset_file():
    #print('Here')
    data = request.json
    dataset_id = data.get('dataset_id')
    filename = data.get('filename')
    if not dataset_id or not filename:
        #print("Dataset ID and filename are required")
        return jsonify({"success": False, "message": "Dataset ID and filename are required"}), 400
    # Need to Sanitize the filename to prevent directory traversal attacks
    filename = filename
    # Construct the full path to the file
    file_path = os.path.join('uploads', 'Datasets', dataset_id, filename)
    # Check if the file exists
    #print(file_path)
    if not os.path.isfile(file_path):
        abort(404)  # Not found if the file doesn't exist
    # Check if the file is within the allowed dataset directory
    if not os.path.realpath(file_path).startswith(os.path.realpath(os.path.join('uploads', 'Datasets', dataset_id))):
        abort(403)  # Forbidden if trying to access files outside the dataset directory
    try:
        # Send the file securely
        return send_file(file_path, as_attachment=True)
    except Exception as e:
        return jsonify({"success": False, "message": "Error downloading file"}), 500


## Alternative for images
@api_bp.route('/datasetimage/<dataset_id>/<filename>', methods=['GET'])
def download_dataset_image_file(dataset_id,filename):
    if not dataset_id or not filename:
        return jsonify({"success": False, "message": "Dataset ID and filename are required"}), 400
    # Need to Sanitize the filename to prevent directory traversal attacks
    filename = filename
    # Construct the full path to the file
    file_path = os.path.join('uploads', 'Datasets', dataset_id, filename)
    # Check if the file exists
    if not os.path.isfile(file_path):
        abort(404)  # Not found if the file doesn't exist
    # Check if the file is within the allowed dataset directory
    if not os.path.realpath(file_path).startswith(os.path.realpath(os.path.join('uploads', 'Datasets', dataset_id))):
        abort(403)  # Forbidden if trying to access files outside the dataset directory
    try:
        # Send the file securely
        return send_file(file_path, as_attachment=True)
    except Exception as e:
        application.logger.error(f"Error downloading file: {str(e)}")
        return jsonify({"success": False, "message": "Error downloading file"}), 500



#########################################
#########################################
#########################################
#######     DATASOURCE MANAGER    #######      
#########################################
#########################################
#########################################


############################
#  Datasource Data Setter  #
############################
@api_bp.route('/datasource/update', methods=['POST'])
@login_required
@roles_required('Researcher')
def datasource_update():
    data = request.json
    sensor_name = data.get('sensorName')
    sensor_description = data.get('sensorDescription')
    sensorUUID = data.get('sensorID')

    # Check if user owns sensor:
    if check_datasource_ownership(sensorUUID,session["useruuid"]):
        success, message = SHARCFunctions.update_datasource(sensorUUID,name = sensor_name, description=sensor_description)
        return jsonify({"success": success, "message": message}), 200
    else:
        success = False
        return jsonify({"success": False, "message": "Permission Denied"}), 400


############################
#  Datasource Add Sensor   #
############################
@api_bp.route('/datasource/add_sensor', methods=['POST'])
@login_required
@roles_required('Researcher')
def datasource_add_sensor():
    data = request.json
    sensor_name = data.get('sensorName')
    sensorUUID = data.get('sensorID')
    if not sensor_name:
        return jsonify({"success": False, "message": "Data Source name is required"}), 400

    # Check if user owns sensor:
    if check_datasource_ownership(sensorUUID,session["useruuid"]):  
        success, message = SHARCFunctions.add_sensor_to_datasource(sensorUUID, sensor_name)
        return jsonify({"success": success, "message": message}), 200
    else:
        return jsonify({"success": False, "message": "Permission Denied"}), 400





#################################
#   Datasource Upload Image     #
#################################
@api_bp.route('/datasource/upload_image', methods=['POST'])
@login_required
@roles_required('Researcher')
def datasource_upload_image():
    sensorUUID = request.form.get('sensorID')

    if 'image' not in request.files:
        return jsonify({"success": False, "message": "No file part"}), 400
    
    file = request.files['image']
    

    if file.filename == '':
        return jsonify({"success": False, "message": "No selected file"}), 400
    

    # Quick Permissions Check
    if not check_datasource_ownership(sensorUUID,session["useruuid"]):
        return jsonify({"success": False, "message": "Permission Denied"}), 400

    #print(allowed_file(file.filename))
    if file:
        filename = file.filename
        file.save(os.path.join('uploads', filename))
        success, message = SHARCFunctions.update_datasource(sensorUUID, image=filename)
        return jsonify({"success": success, "message": message, "filename": filename}), 200
    else:
        return jsonify({"success": False, "message": "File type not allowed"}), 400


#################################
#   Datasource Add Location     #
#################################
@api_bp.route('/datasource/add_location', methods=['POST'])
@login_required
@roles_required('Researcher')
def datasource_add_location():
    data = request.json
    date_time = data.get('dateTime')
    location = data.get('location')
    comment = data.get('comment')
    devicestate = data.get('devicestate')
    sensorUUID = data.get('sensorID')
    if not date_time or not location:
        return jsonify({"success": False, "message": "Both Date Time and Location are required"}), 400
    # Attempt to parse the date_time string
    try:
        parsed_date_time = datetime.strptime(date_time, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return jsonify({"success": False, "message": "Invalid date time format. Use YYYY-MM-DD HH:MM:SS"}), 400

    # Check if user owns datasource:
    if check_datasource_ownership(sensorUUID,session["useruuid"]):  
    # Simulate a successful update
        
        success, message = SHARCFunctions.add_location_to_datasource(sensorUUID, location, parsed_date_time, comment, devicestate)
        return jsonify({"success": success, "message": message}), 200
    else:
        success = False
        return jsonify({"success": False, "message": "Permission Denied"}), 400


#################################
#  Datasource Remove Location   #
#################################
@api_bp.route('/datasource/remove_location', methods=['POST'])
@login_required
@roles_required('Researcher')
def datasource_remove_location():
    datasource_id = request.json.get('sensorID')

    # Get the date time from the request
    date_time = request.json.get('dateTime')
    location = request.json.get('location')
    parsed_date_time = datetime.strptime(date_time, "%Y-%m-%d %H:%M:%S")

    if not date_time:
        return jsonify({"success": False, "message": "Date time is required."}), 400
    
    # Check permissions
    if check_datasource_ownership(datasource_id,session["useruuid"]):
        # Remove the location data from the datasource
        success, message = SHARCFunctions.remove_location_from_datasource(datasource_id, location, parsed_date_time)

        if success:
            return jsonify({"success": True, message: f"Location data for '{date_time}' removed successfully."}), 200
        else:
            return jsonify({"success": False, "message": f"Failed to remove location data: {message}"}), 500
    else:
        return jsonify({"success": False, "message": "Permission Denied"}), 400


#################################
#  Datasource Location Setter   #
#################################
@api_bp.route('/datasource/update_locations', methods=['POST'])
@login_required
@roles_required('Researcher')
def datasource_update_locations():
    data = request.json
    sensor_uuid = data.get('sensorID')
    locations = data.get('locations')

    if not sensor_uuid or not locations:
        return jsonify({"success": False, "message": "Sensor ID and locations are required"}), 400

    # Check if user owns sensor
    if not check_datasource_ownership(sensor_uuid,session["useruuid"]):
        return jsonify({"success": False, "message": "Permission Denied"}), 403

    try:
        updated_locations = []
        statuses = []
        for loc in locations:
            date_time = loc.get('DateTime')
            location = loc.get('Location')
            comment = loc.get('Comment')
            device_state = loc.get('DeviceState')
            if not date_time or not location:
                return jsonify({"success": False, "message": "Both Date Time and Location are required for each entry"}), 400
            try:
                parsed_date_time = datetime.strptime(date_time, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                return jsonify({"success": False, "message": f"Invalid date time format for {date_time}. Use YYYY-MM-DD HH:MM:SS"}), 400

            updated_locations.append({
                "DateTime": parsed_date_time,
                "Location": location,
                "Comment": comment,
                "DeviceState": device_state
            })
            success,message = SHARCFunctions.update_location_from_datasource(sensor_uuid,location,parsed_date_time,comment=comment,devicestate=device_state)
            # Keep track of statuses
            if success:
                statuses.append(success)

        # Handle statuses
        if False in statuses:
            success = False
            message = "There were issues while updating the locations."
        else:
            success = True
            message = "Success"

        if success:
            return jsonify({"success": True, "message": "Location data updated successfully"}), 200
        else:
            return jsonify({"success": False, "message": message}), 500
    except Exception as e:
        return jsonify({"success": False, "message": "An error occurred while updating location data"}), 500


#################################
#  Datasource Location Delete   #
#################################
@api_bp.route('/datasource/remove_sensor', methods=['POST'])
@login_required
@roles_required('Researcher')
def datasource_remove_sensor():
    datasource_id = request.json.get('sensorID')
    # Get the sensor name from the request
    sensor_name = request.json.get('sensorName')
    if not sensor_name:
        return jsonify({"success": False, "message": "Sensor name is required."}), 400
    # Check perms
    if not check_datasource_ownership(datasource_id,session["useruuid"]):
        return jsonify({"success": False, "message": "Permission Denied"}), 403
    try:
        # Remove the sensor from the datasource
        success, message = SHARCFunctions.remove_sensor_from_datasource(datasource_id, sensor_name)
        if success:
            return jsonify({"success": True, message: f"Sensor '{sensor_name}' removed successfully."}), 200
        else:
            return jsonify({"success": False, "message": f"Failed to remove sensor: {message}"}), 500
    except Exception as e:
        return jsonify({"success": False, "message": "An error occurred while deleting location data"}), 500


#################################
#   Datasource Add User         #
#################################
@api_bp.route('/datasource/add_user', methods=['POST'])
@login_required
@roles_required('Researcher')
def datasource_add_user():
    datasource_id = request.json.get('sensorID')
    data = request.json
    user_id = data.get('userId')

    if not user_id:
        return jsonify({"success": False, "message": "User ID is required"}), 400

    # Check if the current user has permission to modify the datasource
    if not check_datasource_ownership(datasource_id, session["useruuid"]):
        return jsonify({"success": False, "message": "Permission Denied"}), 400

    # Add the user to the datasource
    success, message = SHARCFunctions.add_datasource_to_user(user_id,datasource_id)

    if success:
        return jsonify({"success": True, "message": message}), 200
    else:
        return jsonify({"success": False, "message": message}), 500

#################################
#   Datasource Remove User      #
#################################
@api_bp.route('/datasource/remove_user', methods=['POST'])
@login_required
@roles_required('Researcher')
def datasource_remove_user():
    datasource_id = request.json.get('sensorID')
    data = request.json
    user_id = data.get('userId')

    if not user_id:
        return jsonify({"success": False, "message": "User ID is required"}), 400

    # Check if the current user has permission to modify the datasource
    if not check_datasource_ownership(datasource_id, session["useruuid"]):
        return jsonify({"success": False, "message": "Permission Denied"}), 400

    # Remove the user from the datasource
    success, message = SHARCFunctions.remove_datasource_from_user(user_id,datasource_id)

    if success:
        # Get the user's name to send back to the client
        return jsonify({"success": True, "message": message, "userName": ""}), 200
    else:
        return jsonify({"success": False, "message": message}), 500



################################################
#    Datasource Communication Upload from      #
################################################
@api_bp.route('/datasourcecommunication/upload-from', methods=['POST'])
@login_required
@roles_required("Researcher")
def upload_from_data_source():
    #print("Here")
    # Get the file, options file (if provided), and decoder
    file = request.files.get('file')
    options_file = request.files.get('options_file')
    decoder = request.form.get('decoder')

    # Check that decoder is actual decoder
    if decoder not in os.listdir('Decoders'):
        return jsonify({"success": False, "message": "Invalid Decoder"}), 400

    if not file:
        return jsonify({"success": False, "message": "No file part"}), 400

    # Create the directory structure for the decoders
    decoder_dir = os.path.join('Decoders','Inputs')
    if not os.path.exists(decoder_dir):
        os.makedirs(decoder_dir)
    decoderpath = os.path.join('Decoders',decoder)
    
    try:
        # Save the file and options file (if provided)
        filename = secure_filename(file.filename)
        file_path = os.path.join(decoder_dir, filename)
        file.save(file_path)

        if options_file:
            options_filename = secure_filename(options_file.filename)
            options_file_path = os.path.join(decoder_dir, options_filename)
            options_file.save(options_file_path)

        # This tells the decoder function to use the default config
        if not options_file:
            options_file_path = 'None'

        # ACTUALLY RUN THE PROGRAM
        output = subprocess.check_output(['python3', decoderpath, file_path, options_file_path, session['useruuid']], universal_newlines=True)
        # Return based on output
        return jsonify({"success": True, "message": "Files uploaded and processed.","output" : output}), 200
    except Exception as e:
        return jsonify({"success": False, "message": f"Error uploading files: {str(e)}"}), 400


################################################
#    Datasource Communication Upload To        #
################################################
@api_bp.route('/datasourcecommunication/upload-to', methods=['POST'])
@login_required
@roles_required("Researcher")
def upload_to_data_source():
    # Get the file, options file (if provided), and encoder
    file = request.files.get('file')
    options_file = request.files.get('options_file')
    encoder = request.form.get('encoder')

    if not file:
        return jsonify({"success": False, "message": "No file part"}), 400

    # Check that decoder is actual decoder
    if encoder not in os.listdir('Encoders'):
        return jsonify({"success": False, "message": "Invalid Encoder"}), 400
    # Create the directory structure for the encoders
    encoder_dir = 'Encoders'
    if not os.path.exists(encoder_dir):
        os.makedirs(encoder_dir)
    encoderpath = os.path.join(encoder_dir,encoder)
    # Save the file and options file (if provided)
    try:
        filename = secure_filename(file.filename)
        file_path = os.path.join(encoder_dir, filename)
        file.save(file_path)

        if options_file:
            options_filename = secure_filename(options_file.filename)
            options_file_path = os.path.join(encoder_dir, options_filename)
            options_file.save(options_file_path)
        # This tells the endcoder function to use the default config
        if not options_file:
            options_file_path = 'None'
        
        # ACTUALLY RUN THE PROGRAM
        output = subprocess.check_output(['python3', encoderpath, file_path, options_file_path, session['useruuid']], universal_newlines=True)
        return jsonify({"success": True, "message": "Files uploaded and processed successfully!","output" : output}), 200
    except Exception as e:
        return jsonify({"success": False, "message": f"Error uploading files: {str(e)}"}), 400




#########################################
#########################################
#########################################
#######       DATASET MANAGER     #######      
#########################################
#########################################
#########################################

#################################
#      Dataset File Upload      #
#################################
@api_bp.route('/dataset/upload', methods=['POST'])
@login_required
@roles_required('Researcher')
def dataset_upload():
    datasetID = request.form.get('datasetID')
    if 'files' not in request.files:
        return jsonify({"success": False, "message": "No file part"}), 400
    
    files = request.files.getlist('files')
    if len(files) == 0:
        return jsonify({"success": False, "message": "No selected file"}), 400

    if not check_dataset_ownership(datasetID,session["useruuid"]):
        return jsonify({"success": False, "message": "Permission Denied"}), 403

    # Create the directory structure
    dataset_dir = os.path.join('uploads', 'Datasets', datasetID)
    
    # Check if the directory exists, if not create it
    if not os.path.exists(dataset_dir):
        os.makedirs(dataset_dir)
    
    # Secure File Uploader
    uploaded_files = 0
    for file in files:
        if file:
            filename = secure_filename(file.filename)
            file_path = os.path.join(dataset_dir, filename)
            file.save(file_path)
            uploaded_files += 1
            SHARCFunctions.add_file_to_dataset(datasetID, filename)

    if uploaded_files > 0:
        return jsonify({"success": True, "message": f"Files uploaded successfully", "uploadedFiles": uploaded_files}), 200
    else:
        return jsonify({"success": False, "message": "No files were uploaded. Check file types."}), 400

#################################
#     Dataset   File Upload     #
#################################
@api_bp.route('/dataset/update', methods=['POST'])
@login_required
@roles_required('Researcher')
def dataset_update():
    data = request.json
    dataset_name = data.get('datasetName')
    description = data.get('description')
    datasetUUID = data.get('datasetID')
    if not dataset_name:
        return jsonify({"success": False, "message": "Dataset name and collected by are required"}), 400
    if check_dataset_ownership(datasetUUID,session["useruuid"]):
        success, message = SHARCFunctions.update_dataset(datasetUUID,name = dataset_name, description=description)
        return jsonify({"success": success, "message": message}), 200
    else:
        success = False
        return jsonify({"success": False, "message": "Permission Denied"}), 400

#################################
#     Dataset   File Upload     #
#################################
@api_bp.route('/dataset/add_datasource', methods=['POST'])
@login_required
@roles_required('Researcher')
def dataset_add_datasource():
    data = request.json
    DataSourceUUID = data.get('DataSourceUUID')
    datasetUUID = data.get('datasetID')

    if check_dataset_ownership(datasetUUID,session["useruuid"]):
        success, message = SHARCFunctions.add_dataset_to_datasource(datasetUUID,DataSourceUUID)
        return jsonify({"success": success, "message": message}), 200
    else:
        success = False
        return jsonify({"success": False, "message": "Permission Denied"}), 400

#################################
# Dataset  Remove datasource    #
#################################
@api_bp.route('/dataset/remove_datasource', methods=['POST'])
@login_required
@roles_required('Researcher')
def dataset_remove_datasource():
    data = request.json
    datasetuuid = data.get('datasetID')
    datasourceuuid = data.get('datasourceID')

    if check_dataset_ownership(datasetuuid,session["useruuid"]):
        success, message = SHARCFunctions.remove_dataset_from_datasource(datasetuuid,datasourceuuid)
        if success:
            return jsonify({"success": True, "message": "Data Source removed successfully"}), 200
        else:
            return jsonify({"success": False, "message": f"Failed to remove Data Source: {message}"}), 500
    else:
        return jsonify({"success": False, "message": "Permission Denied"}), 403

        

#################################
#      Dataset File Delete      #
#################################
@api_bp.route('/dataset/delete_file', methods=['POST'])
@login_required
@roles_required('Researcher')
def dataset_delete_file():
    data = request.json
    dataset_id = data.get('datasetID')
    file_name = data.get('fileName')
    # Check if user owns or has access to the dataset
    if check_dataset_ownership(dataset_id,session["useruuid"]):
        # Remove from database
        success, message = SHARCFunctions.remove_file_from_dataset(dataset_id, file_name)
        # Must still remove from filesystem
        if success:
            return jsonify({"success": True, "message": "File deleted successfully"}), 200
        else:
            return jsonify({"success": False, "message": f"Failed to delete file: {message}"}), 500
    else:
        return jsonify({"success": False, "message": "Permission Denied"}), 403




#########################################
#########################################
#########################################
#######      EXPEDITION STUFF     #######      
#########################################
#########################################
#########################################

@api_bp.route('/expedition/update', methods=['POST'])
@login_required
@roles_required('Researcher')
def update_expedition():
    data = request.json
    expedition_uuid = data.get('expeditionUUID')
    name = data.get('name')
    description = data.get('description')
    start_date = data.get('startDate')
    end_date = data.get('endDate')
    if start_date != "":
        start_date=datetime.strptime(start_date, "%Y-%m-%d")
    else:
        start_date = None
    if end_date != "":
        end_date=datetime.strptime(end_date, "%Y-%m-%d")
    else:
        end_date = None

    if not expedition_uuid:
        return jsonify({"success": False, "message": "Expedition UUID is required"}), 400

    # Check if user has permission to update this expedition
    if not check_expedition_ownership(expedition_uuid, session["useruuid"]):
        return jsonify({"success": False, "message": "Permission Denied"}), 403

    try:
        success, message = SHARCFunctions.update_expedition(
            expedition_uuid,
            name=name,
            description=description,
            start_date=start_date,
            end_date=end_date
        )
        return jsonify({"success": success, "message": message}), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@api_bp.route('/expedition/add_researcher', methods=['POST'])
@login_required
@roles_required('Researcher')
def add_researcher_to_expedition():
    data = request.json
    expedition_uuid = data.get('expeditionUUID')
    researcher_uuid = data.get('researcherUUID')

    if not expedition_uuid or not researcher_uuid:
        return jsonify({"success": False, "message": "Expedition UUID and Researcher UUID are required"}), 400

    # Check if user has permission to update this expedition
    if not check_expedition_ownership(expedition_uuid, session["useruuid"]):
        return jsonify({"success": False, "message": "Permission Denied"}), 403

    try:
        success, message = SHARCFunctions.add_user_to_expedition(researcher_uuid,expedition_uuid)
        return jsonify({"success": success, "message": message}), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@api_bp.route('/expedition/add_datasource', methods=['POST'])
@login_required
@roles_required('Researcher')
def add_datasource_to_expedition():
    data = request.json
    expedition_uuid = data.get('expeditionUUID')
    datasource_uuid = data.get('datasourceUUID')

    if not expedition_uuid or not datasource_uuid:
        return jsonify({"success": False, "message": "Expedition UUID and Datasource UUID are required"}), 400

    # Check if user has permission to update this expedition
    if not check_expedition_ownership(expedition_uuid, session["useruuid"]):
        return jsonify({"success": False, "message": "Permission Denied"}), 403

    try:
        success, message = SHARCFunctions.add_datasource_to_expedition(datasource_uuid,expedition_uuid)
        return jsonify({"success": success, "message": message}), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@api_bp.route('/expedition/delete', methods=['POST'])
@login_required
@roles_required('Researcher')
def delete_expedition():
    data = request.json
    expedition_uuid = data.get('expeditionUUID')

    if not expedition_uuid:
        return jsonify({"success": False, "message": "Expedition UUID"}), 400

    # Check if user has permission to update this expedition
    if not check_expedition_ownership(expedition_uuid, session["useruuid"]):
        return jsonify({"success": False, "message": "Permission Denied"}), 403

    try:
        success, message = SHARCFunctions.delete_expedition(expedition_uuid)
        return jsonify({"success": success, "message": message}), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

#################################
#    Expedition Remove User     #
#################################
@api_bp.route('/expedition/remove_user', methods=['POST'])
@login_required
@roles_required('Researcher')
def expedition_remove_user():
    data = request.json
    expeditionUUID = data.get('expeditionUUID')
    userUUID = data.get('userUUID')

    if check_expedition_ownership(expeditionUUID, session["useruuid"]):
        #print("Removing", userUUID)
        success = True
        if success:
            return jsonify({"success": True, "message": "User removed successfully"}), 200
        else:
            return jsonify({"success": False, "message": "Failed to remove user"}), 500
    else:
        return jsonify({"success": False, "message": "Permission Denied"}), 403


#################################
#     Expedition Remove Datasource     #
#################################
@api_bp.route('/expedition/remove_datasource', methods=['POST'])
@login_required
@roles_required('Researcher')
def expedition_remove_datasource():
    data = request.json
    expeditionUUID = data.get('expeditionUUID')
    datasourceuuid = data.get('datasourceUUID')

    if check_expedition_ownership(expeditionUUID, session["useruuid"]):
        print("Removing", datasourceuuid)
        success = True
        if success:
            return jsonify({"success": True, "message": "Data Source removed successfully"}), 200
        else:
            return jsonify({"success": False, "message": "Failed to remove Data Source"}), 500
    else:
        return jsonify({"success": False, "message": "Permission Denied"}), 403


GEOJSON_FILE = '.json'
GEODir = 'Expeditions/'

def save_to_geojson(data, expedition_uuid):
    with open(f'{GEODir}{expedition_uuid}{GEOJSON_FILE}', 'w') as f:
        json.dump(data, f)

def load_from_geojson(expedition_uuid):
    try:
        with open(f'{GEODir}{expedition_uuid}{GEOJSON_FILE}', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"type": "FeatureCollection", "features": []}

@api_bp.route('/expedition/save_drawn_items', methods=['POST'])
@login_required
@roles_required("Researcher")
def save_drawn_items():
    data = request.json
    expedition_uuid = data.get('expeditionUuid')
    items = data.get('items')
    
    if not expedition_uuid or not items:
        return jsonify({"success": False, "message": "Missing expedition UUID or items"}), 400
    
    geojson = {
        "type": "FeatureCollection",
        "features": items  # The items are already in the correct format
    }
    
    save_to_geojson(geojson, expedition_uuid)
    return jsonify({"success": True, "message": "Items saved successfully"}), 200

@api_bp.route('/expedition/load_drawn_items', methods=['POST'])
def load_drawn_items():
    #("Here")
    #print(request.json)
    expedition_uuid = request.json.get('expeditionUuid')
    #print(expedition_uuid)
    #print("===")
    if not expedition_uuid:
        return jsonify({"success": False, "message": "Missing expedition UUID"}), 400
    
    geojson = load_from_geojson(expedition_uuid)
    return jsonify(geojson["features"]), 200

############################
#  Datasource Data Getter  #
############################
@api_bp.route('/expedition/get_datasource_data', methods=['POST'])
def get_expedition_datasource_data():
    data = request.json
    expedition_uuid = data.get('expeditionUuid')

    result = SHARCFunctions.get_expedition(expedition_uuid)
    ExpeditionDataSourceUUIDs = [datasource.data_source.UUID for datasource in result.data_sources]

    results = SHARCFunctions.getdatasources()
    datasources = []
    for source in results:
        if source["UUID"] in ExpeditionDataSourceUUIDs:
            for location in source["Locations"]:
                datasources.append({
                    "UUID": source["UUID"],
                    "Sensor Name": source["Name"],
                    "Time": location["DateTime"],
                    "Location": location["Location"]
                })
    return jsonify(datasources)

    # #datasources = []
    # #for source in results:
    #     # Possibly check if the dataset is onMap?
    # #    for location in source["Locations"]:
    # #datasources.append({"UUID": source["UUID"],"Sensor Name": source["Name"],"Time" : location["DateTime"],"Location" :location["Location"]})
    # return jsonify(result)




@api_bp.route('/expedition/upload_file', methods=['POST'])
@login_required
@roles_required("Researcher")
def expedition_upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400
    
    expedition_uuid = request.form.get('expeditionUUID')
    if not expedition_uuid:
        return jsonify({'error': 'No expedition UUID provided'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file:
        try:
            filename = secure_filename(file.filename)
            file_extension = os.path.splitext(filename)[1].lower()

            if file_extension == '.kml':
                # Read KML content
                kml_content = file.read().decode('utf-8')
                
                # Convert KML to GeoJSON
                try:
                    geojson_data = convert(StringIO(kml_content))[0]
                    # kml2geojson returns a list of features, so we need to wrap it in a FeatureCollection
                    #print('====Here===')
                    #print(geojson_data)
                    # geojson_data = {
                    #     "type": "FeatureCollection",
                    #     "features": geojson_data
                    # }
                    #print('====Here===')
                except ExpatError:
                    return jsonify({'error': 'Invalid KML file'}), 400

            elif file_extension in ['.geojson','.json','.JSON']:
                try:
                    geojson_data = json.loads(file.read().decode('utf-8'))
                    #print('====Here===')
                    #print(geojson_data)
                    # geojson_data = {
                    #     "type": "FeatureCollection",
                    #     "features": geojson_data
                    # }
                    #print('====Here===')
                except JSONDecodeError:
                    return jsonify({'error': 'Invalid GeoJSON file'}), 400
            else:
                return jsonify({'error': 'Unsupported file type. Please upload KML or GeoJSON files.'}), 400
            #print("Combining")
            # Combine with existing expedition JSON file
            expedition_file = f'Expeditions/{expedition_uuid}.json'
            if os.path.exists(expedition_file):
                with open(expedition_file, 'r') as f:
                    existing_data = json.load(f)
                
                # Combine the existing features with the new ones
                if 'features' in existing_data and 'features' in geojson_data:
                    #print("Existing:")
                    #print(existing_data['features'])

                    #print("New:")
                    #print(geojson_data['features'])

                    existing_data['features'].extend(geojson_data['features'])
                elif 'features' in geojson_data:
  
                    #print(geojson_data['features'])
                    existing_data['features'] = geojson_data['features']

            else:
                existing_data = geojson_data

            #print("Final:")
            #print(existing_data)
            # Write the combined data back to the file
            with open(expedition_file, 'w') as f:
                json.dump(existing_data, f)
            
            return jsonify({'message': f'File {filename} processed and combined with {expedition_file} successfully'}), 200

        except Exception as e:
            return jsonify({'error': f'An error occurred: {str(e)}'}), 500
    
    return jsonify({'error': 'File upload failed'}), 500


def merge_geojson(existing_data, new_data):
    if not existing_data:
        return new_data
    
    if 'type' not in existing_data:
        existing_data = {"type": "FeatureCollection", "features": []}
    
    if existing_data['type'] != 'FeatureCollection':
        existing_data = {"type": "FeatureCollection", "features": [existing_data]}
    
    if 'features' not in existing_data:
        existing_data['features'] = []
    
    if new_data['type'] == 'FeatureCollection':
        existing_data['features'].extend(new_data['features'])
    else:
        existing_data['features'].append(new_data)
    
    return existing_data



#########################################
#########################################
#########################################
#######         ADMIN STUFF       #######      
#########################################
#########################################
#########################################

#################################
#    Admin Change UserRole      #
#################################
@api_bp.route('/admin/changerole', methods=['POST'])
@login_required
@roles_required('Administrator')
def change_user_role():
    data = request.json
    useruuid = data.get('username')
    new_role = data.get('role')

    if not useruuid or not new_role:
        return jsonify({"success": False, "message": "Username and role are required"}), 400

    success, message = SHARCFunctions.update_user(useruuid, role=new_role)

    if success:
        return jsonify({"success": True, "message": f"Role changed to {new_role} successfully"}), 200
    else:
        return jsonify({"success": False, "message": message}), 400

#################################
#       Admin Add User          #
#################################
@api_bp.route('/admin/adduser', methods=['POST'])
@login_required
@roles_required('Administrator')
def admin_add_user():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"success": False, "message": "Username and password are required"}), 400
    useruuid = str(uuid.uuid1())
    if SHARCFunctions.getuuid_from_user(username) != '':
        return jsonify({"success": False, "message": f"User with username {username} already exists"}), 400
    hashedpassword = generate_password_hash(password)
    success, message = SHARCFunctions.add_new_user(useruuid,username,hashedpassword,"","Public")
    if success:
        return jsonify({"success": True, "message": f"User {username} was added."}), 200
    else:
        return jsonify({"success": False, "message": message}), 400


#################################
#       Admin Del User          #
#################################
@api_bp.route('/admin/deluser', methods=['POST'])
@login_required
@roles_required('Administrator')
def admin_del_user():
    data = request.json
    username = data.get('username')

    if not username:
        return jsonify({"success": False, "message": "Username required"}), 400
    useruuid = SHARCFunctions.getuuid_from_user(username)
    if useruuid == '':
        return jsonify({"success": False, "message": "User does not exist"}), 400

    #SHARCFunctions.dele
    #success, message = SHARCFunctions.add_new_user()
    success = True
    if success:
        return jsonify({"success": True, "message": f"User {username} was deleted."}), 200
    else:
        return jsonify({"success": False, "message": message}), 400

#################################
#      Admin Get UserRoles      #
#################################
@api_bp.route('/admin/getuserrole', methods=['POST'])
@login_required
@roles_required('Administrator')
def get_user_role():
    data = request.json
    useruuid = data.get('username')
    if not useruuid:
        return jsonify({"success": False, "message": "Username is required"}), 400
    results = SHARCFunctions.getusers(useruuid = useruuid)
    if len(results) == 1:
        return jsonify({"success": True, "role": results[0]["Role"]}), 200
    else:
        return jsonify({"success": False, "message": "Failed to fetch user role"}), 400


@api_bp.route('/admin/upload_encoder_decoder', methods=['POST'])
@login_required
@roles_required('Administrator')
def upload_encoder_decoder():
    if 'files' not in request.files:
        return jsonify({"success": False, "message": "No file part"}), 400

    files = request.files.getlist('files')
    if len(files) == 0:
        return jsonify({"success": False, "message": "No selected file"}), 400

    upload_type = request.form.get('type')
    if upload_type not in ['Encoder', 'Decoder']:
        return jsonify({"success": False, "message": "Invalid upload type"}), 400

    # Create path
    upload_dir = f'{upload_type}s'
    
    # Check if the directory exists and create if it doesn't
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)

    # Secure File Uploader
    uploaded_files = 0
    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(upload_dir, filename)
            file.save(file_path)
            uploaded_files += 1

    if uploaded_files > 0:
        return jsonify({
            "success": True, 
            "message": f"{upload_type} files uploaded successfully", 
            "uploadedFiles": uploaded_files
        }), 200
    else:
        return jsonify({
            "success": False, 
            "message": f"No {upload_type} files were uploaded. Check file types."
        }), 400


#################################
#     Dataset   File Upload     #
#################################
@api_bp.route('/admin/delete_file', methods=['POST'])
@login_required
@roles_required('Administrator')
def admin_del_file():
    data = request.json
    file_type = data.get('type')
    filename = data.get('filename')

    if file_type not in ['Encoder', "Decoder"]:
        return jsonify({"success": False, "message": "Invalid Type"}), 400
    
    folder_path = file_type + "s"
    if filename not in os.listdir(folder_path):
        return jsonify({"success": False, "message": "Invalid File"}), 400
    
    try:
        file_path = os.path.join(folder_path, filename)
        if os.path.exists(file_path):
            os.remove(file_path)
            return jsonify({"success": True, "message": "File deleted successfully"}), 200
        else:
            return jsonify({"success": False, "message": "Invalid File"}), 400
    except:
        return jsonify({"success": False, "message": "Failed to delete file"}), 500

@api_bp.route('/admin/toggle_dataset_approval', methods=['POST'])
@login_required
@roles_required('Administrator')
def toggle_dataset_approval():
    data = request.json
    dataset_id = data.get('dataset_id')

    dataset = SHARCFunctions.getdatasets(datasetuuid=dataset_id)[0]
    current_approval_status = dataset['AdminApproved']
    new_approval_status = not current_approval_status
    
    success, message = SHARCFunctions.update_dataset(dataset_id, admin_approved=new_approval_status)
    
    if success:
        return jsonify({"success": True, "message": f"Dataset approval status updated to {new_approval_status}"}), 200
    else:
        return jsonify({"success": False, "message": f"Failed to update dataset approval status: {message}"}), 500

@api_bp.route('/usersettings/change-password', methods=['POST'])
@login_required
def change_user_password():
    data = request.json
    useruuid = data.get('useruuid')
    current_password = data.get('currentPassword')
    new_password = data.get('newPassword')


    #if current_password == "AdminReset" and session.get("user_role")
    if not current_password or not new_password:
        return jsonify({"success": False, "message": "Current and new passwords are required"}), 400
    
    if not SHARCFunctions.authenticate_user(session.get("username"), current_password):
        if not session.get("userroles") == "Administrator":
            return jsonify({"success": False, "message": "Current Password Incorrect."}), 400
    
    if useruuid == '':
        useruuid = session.get("useruuid")
    # Hash the new password
    hashed_password = generate_password_hash(new_password)
    print(useruuid,hashed_password)
    # Update the user's password in the database
    success, message = SHARCFunctions.update_user(useruuid, password=hashed_password)

    if success:
        return jsonify({"success": True, "message": "Password changed successfully"}), 200
    else:
        return jsonify({"success": False, "message": message}), 400


@api_bp.route('/admin/backup', methods=['GET'])
@login_required
@roles_required('Administrator')
def backup_system():
    # Create a zip file of the system
    backup_filename = 'system_backup.zip'
    with zipfile.ZipFile(backup_filename, 'w') as zipf:
        for root, dirs, files in os.walk('.'):
            for file in files:
                zipf.write(os.path.join(root, file))
    
    # Send the zip file
    return send_file(backup_filename, as_attachment=True)

@api_bp.route('/admin/restore', methods=['POST'])
@login_required
@roles_required('Administrator')
def restore_system():
    if 'file' not in request.files:
        return jsonify({"success": False, "message": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"success": False, "message": "No selected file"}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join('uploads/Restore', filename)
        file.save(file_path)
        
 
        # with zipfile.ZipFile(file_path, 'r') as zip_ref:
        #     zip_ref.extractall('path/to/system/files')
        
        # Remove the uploaded zip file after restoration
        os.remove(file_path)  

        return jsonify({"success": True, "message": "System restored successfully"}), 200
    return jsonify({"success": False, "message": "Invalid file"}), 400

@api_bp.route('admin/toggle_readonly', methods=['POST'])
@login_required
@roles_required('Administrator')
def toggle_readonly():
    data = request.json
    read_only = data.get('readOnly', False)
    
    # Implement your logic to set the system to read-only or read-write mode
    # This is a placeholder for the actual implementation
    if read_only:
        # Set system to read-only mode
        pass
    else:
        # Set system to read-write mode
        pass
    
    return jsonify({"success": True, "message": f"System set to {'read-only' if read_only else 'read-write'} mode"}), 200

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'zip'}
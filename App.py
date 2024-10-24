import sys, os, datetime, time, glob, sqlite3, subprocess, uuid, binascii, traceback, csv,json
#import resource, signal, stat, inspect
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
application = Flask(__name__)

#application config settings regarding flask stuff 
application.config['SECRET_KEY'] = '\x1b\xc0\xc6\x08|\xe1\xa2\x0e\xe7\xee,7AW5k\x17c}1\xbf\x96q\r'
application.config['BASIC_AUTH_FORCE'] = True
SESSION_TYPE = 'filesystem'
application.config.from_object(__name__)
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif','csv'}
application.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

Session(application)
############################################
#                  DANGER                  #
############################################
BYPASS_PASSWORD = False  #SECURITY RISK, MUST BE SET TO False UNLESS NEEDED FOR TESTING PURPOSES
BYPASS_GROUPS   = False  #SECURITY RISK, MUST BE SET TO False UNLESS NEEDED FOR TESTING PURPOSES
DEBUG = True    
############################################


############################################
#             Auth/Perms Functions         #
############################################
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        try:
            if session.get('logged_in'):            
                return f(*args, **kwargs)
            else:
                return redirect(url_for('loginsite'))
        except:

            if DEBUG:
                return f(*args, **kwargs)     # enable this to show template errors
            return redirect(url_for('loginsite'))
    return wrap

def roles_required(funcname):
    def groupsthings(f):
        @wraps(f)
        def wrap(*args, **kwargs):
            if check_groups(funcname): 
                return f(*args, **kwargs)
            else:
                return redirect(url_for('home'))
        return wrap
    return groupsthings

def check_groups(group):
    if BYPASS_GROUPS:
        return True 
    if group == session.get('userroles'):
        return True
    if 'Administrator' == session.get('userroles'):
        return True
    return False 

def hash_function(password,salt):
    return(password)

############################################
############################################
############################################
###             ROUTING                  ###
############################################
############################################
############################################


####################
#     Home Page    #
####################
@application.route('/')
def home():
    # Potential Logic
    return(render_template('Home.html',Logged_in=session.get('logged_in'),
    Username = session.get('username')))



####################
#    Login Page    #
####################
@application.route('/login',methods = ['POST','GET'])
def loginsite():
    if request.method == 'POST':
        user = request.form['Username']
        Password = request.form['Password']
        if SHARCFunctions.authenticate_user(user,Password):
            session['username'] = user
            # session['useruuid']= SHARCFunctions.authenticate_user(user,Password)
            useruuid = SHARCFunctions.getuuid_from_user(user)
            session['useruuid'] = useruuid
            userresult = SHARCFunctions.getusers(useruuid=useruuid)
            print(userresult)
            print(userresult[0])
            print(userresult[0]["Role"])
            session['userroles'] = userresult[0]["Role"]
            session['logged_in'] = True 
            session.permanent = True
            return redirect(url_for('home'))
        else:
            session['logged_in'] = False
            session['userroles'] = ''
            return render_template('Login.html',Logged_in=session.get('logged_in'),
            Username = session.get('username'))
            
    return render_template('Login.html',Logged_in=session.get('logged_in'),
    Username = session.get('username'))


####################
# Logout Redirect  #
####################
@application.route('/logout')
@login_required
def logout():
    session['username'] = ''
    session['useruuid'] = ''
    session['userroles'] = ''
    session['logged_in'] = False

    return(redirect(url_for('home')))



####################
# Data Search Page #
####################
@application.route('/datasearch',methods = ['POST','GET'])
def DataSearch():
    if request.method == 'POST':
        data = request.form
        TextSearch = (data['TextSearch'])
        TextBool = False
        StartBool = False
        EndBool = False
        if TextSearch != "":
            TextBool = True
        
        try:
            startdate = (data['startdate'])
            enddate = (data['enddate'])
            parsed_startdate = datetime.strptime(startdate, "%Y-%m-%d")
            parsed_enddate = datetime.strptime(enddate, "%Y-%m-%d")
            StartBool = True
            EndBool = True
        except:
            parsed_startdate = datetime.now()
            parsed_enddate = datetime.now()
            StartBool = False
            EndBool = False

        results = SHARCFunctions.getdatasets()
        filtered_results = []
        for result in results:
            Add = False
            if TextBool: 
                if  TextSearch in result['Name']:
                    Add = True
                try:
                    if TextSearch in result['Description']:
                        Add = True 
                except:
                    print("None Description")
            else: 
                Add = True
            if  StartBool and EndBool:
                if not (parsed_startdate < result['DateAdded'] <  parsed_enddate):
                    Add = False
            if not result["AdminApproved"]:
                Add = False
            if Add:
                filtered_results.append(result)

        #print(filtered_results[0].Datasource)
        return(render_template('DatasetSearch.html',Logged_in=session.get('logged_in'),
        Username = session.get('username'),
        results = filtered_results))
    # Return all

    results = SHARCFunctions.getdatasets()
    filtered_results = []
    for result in results:
        if result["AdminApproved"]:
            filtered_results.append(result)
    return(render_template('DatasetSearch.html',Logged_in=session.get('logged_in'),
    Username = session.get('username'),
    results = filtered_results))



#####################
# Data Manager Page #
#####################
@application.route('/datamanager')
@login_required
@roles_required('Researcher')
def DataManager():
    # Need to fix this
    results = SHARCFunctions.getdatasets(useruuid=session['useruuid'])
    datasources = SHARCFunctions.getdatasources(useruuid=session['useruuid'])
    return(render_template('DatasetManager.html',Logged_in=session.get('logged_in'),
    Username = session.get('username'),
    results = results,
    datasources=datasources))



#####################
# Data Editor Page  #
#####################
@application.route('/dataeditor/<dataset>')
@login_required
@roles_required('Researcher')
def DataEditor(dataset):
    
    result = SHARCFunctions.getdatasets(useruuid=session["useruuid"], datasetuuid=dataset)
    # If 0 or more than 1 there is an issue
    if len(result) != 1:
        return redirect(url_for('DatasetManager'))
    else:
        result = result[0]

    # Get available data sources
    available_data_sources = SHARCFunctions.getdatasources(useruuid=session["useruuid"])
    # Find the current data source name
    current_datasource_name = ""
    for data_source in available_data_sources:
        if data_source["UUID"] == result.get("DataSourceUUID"):
            current_datasource_name = data_source["Name"]
            break
    
    users = SHARCFunctions.getusers()
    return render_template('DatasetEditor.html',
                           Logged_in=session.get('logged_in'),
                           Username=session.get('username'),
                           dataset=result,
                           available_data_sources=available_data_sources,
                           current_datasource_name=current_datasource_name)

@application.route('/datasetcreator/<datasourceuuid>')
@login_required
@roles_required('Researcher')
def DatasetCreator(datasourceuuid):
    # MUST CHECK DATASOURCE PERMS STILL
    # Generate a new UUID for the dataset
    newdatasetuuid = str(uuid.uuid1())
    # Add the new dataset
    success, message = SHARCFunctions.add_new_dataset(newdatasetuuid, "New Dataset Name")        
    if not success:
        flash(f"Error creating new dataset: {message}", "error")
        return redirect(url_for('DataManager'))
    # Add the dataset to the datasource
    success, message = SHARCFunctions.add_dataset_to_datasource(newdatasetuuid,datasourceuuid)
    if not success:
        flash(f"Error associating dataset with user: {message}", "error")
        return redirect(url_for('DataManager'))
    # Redirect to the data editor page for the new dataset
    SHARCFunctions.add_new_log(str(uuid.uuid1()), datetime.now(),session["useruuid"],"User Created New Dataset",result_text=message)
    return redirect(url_for('DataEditor', dataset=newdatasetuuid))

#######################
# Data Download Page  #
#######################
@application.route('/datadownload/<dataset>')
def DataDownload(dataset):
    result = {}
    if session.get('roles') == None:
        results = SHARCFunctions.getdatasets(datasetuuid=dataset)
    else:
        if session.get('roles').split(",").contains("Administrator"):
            results = SHARCFunctions.getdatasets(datasetuuid=dataset)
        elif session.get('roles').split(",").contains("Researcher"):
            results = SHARCFunctions.getdatasets(useruuid=session["UUID"],datasetuuid=dataset)
    # If 0 or more than 1 there is an issue
    if len(results) != 1:
        return redirect(url_for('DataSearch'))
    else:
        result = results[0]

    # Get image names for image displayer
    Images = []
    hasImages = False
    for file in result["Files"]:
        if file[1].split(".")[-1] in ["png","jpg","jpeg"]:
            Images.append((dataset,file[1]))
            hasImages = True
    
    return render_template('DatasetDownload.html',
                           Logged_in=session.get('logged_in'),
                           Username=session.get('username'),
                           dataset=result,
                           hasImages = hasImages,
                           Images=Images)


#########################
# DataSource Admin Page #
#########################
@application.route('/datasourceadmin',methods = ['POST','GET'])
@login_required
@roles_required('Researcher')
def DatasourceAdmin():

    results = SHARCFunctions.getdatasources(useruuid = session.get("useruuid"))
    return render_template('DataSourceManager.html', Logged_in=session.get('logged_in'),
    Username = session.get('username'), datasources = results)



#################################
# DataSource Communication Page #
#################################
@application.route('/datasourcecommunication',methods = ['POST','GET'])
@login_required
@roles_required('Researcher')
def Datasourcecommunication():
    decoders = ["SHARC_Decoder.py"]
    encoders = ["SHARC_Encoder.py"]
    return render_template('DataSourceCommunication.html', Logged_in=session.get('logged_in'),
    Username = session.get('username'), decoders = decoders,encoders = encoders)


#################################
#   Administration Tools Page   #
#################################
@application.route('/admintools',methods = ['POST','GET'])
@login_required
@roles_required('Administrator')
def AdminTools():

    datasets = SHARCFunctions.getdatasets()
    users = SHARCFunctions.getusers()
    activity_log = SHARCFunctions.get_logs()

    # Construct dictionarys of results for frontend
    userresults = [{"Username": user["UserName"], "UserUUID": user["UUID"]} for user in users]
    datasetresults = []
    for dataset in datasets:
        dataset_contributors = []
        for user in users:
            if any(ds['UUID'] == dataset['UUID'] for ds in datasets):
                dataset_contributors.append(user['UserName'])
        datasetresults.append({
            "DatasetName": dataset['Name'],
            "DatasetUUID": dataset['UUID'],
            "DatasetContributers": dataset_contributors,
            "DatasetApproved": dataset['AdminApproved']
        })
    encoders = [encoder for encoder in os.listdir('Encoders') if os.path.isfile(os.path.join('Encoders',encoder))]
    #print(encoders)
    decoders = [decoder for decoder in os.listdir('Decoders') if os.path.isfile(os.path.join('Decoders',decoder))]
    return render_template('AdminTools.html', Logged_in=session.get('logged_in'),
    Username = session.get('username'), users = userresults, datasets = datasetresults,
    log = activity_log,encoders = encoders,decoders = decoders)

#################################
#   Administration Tools Page   #
#################################
@application.route('/profile',methods = ['POST','GET'])
@login_required
def Profile():

    activity_log = SHARCFunctions.get_logs(session["useruuid"])
    user = session.get("useruuid")
    return render_template('UserSettings.html', Logged_in=session.get('logged_in'),
    Username = session.get('username'),
    log = activity_log)


######################
# Sensor Editor Page #
######################
@application.route('/datasourceeditor/<datasource>')
@login_required
@roles_required('Researcher')
def DatasourceEditor(datasource):
    # If the user has clicked the new button they will come here
    if datasource == "new":
        # Generate a new UUID for the datasource
        newdatasourceuuid = str(uuid.uuid1())
        # Add the new datasource
        success, message = SHARCFunctions.add_new_datasource(newdatasourceuuid, "New Datasource Name")
        if not success:
            flash(f"Error creating new datasource: {message}", "error")
            return redirect(url_for('DataSourceAdmin'))
        # Add the datasource to the user
        success, message = SHARCFunctions.add_datasource_to_user(session["useruuid"], newdatasourceuuid)
        if not success:
            flash(f"Error associating datasource with user: {message}", "error")
            return redirect(url_for('DatasourceAdmin'))
        # Redirect to the sensor editor page for the new sensor
        SHARCFunctions.add_new_log(str(uuid.uuid1()), datetime.now(),session["useruuid"],"User Created New DataSource",result_text=message)
        return redirect(url_for('DatasourceEditor', datasource=newdatasourceuuid))
    # Otherwise for existing sensors, proceed as before
    try:
        result = SHARCFunctions.getdatasources(useruuid=session["useruuid"], datasourceuuid=datasource)[0]
    except IndexError:
        flash("Sensor not found or you don't have permission to access it.", "error")
        return redirect(url_for('DatasourceAdmin'))

    sorted_locations = sorted(result['Locations'], key=lambda x: x['DateTime'])
    sorted_locations.reverse()
    users = SHARCFunctions.getusers()
    return render_template('DataSourceEditor.html',
                           Logged_in=session.get('logged_in'),
                           Username=session.get('username'),
                           datasource=result,
                           sorted_locations = sorted_locations,
                           all_users=users)


#########################
# Dataset Deleter Route #
#########################
@application.route('/dataeditor/<datasetID>/delete')
@login_required
@roles_required('Researcher')
def delete_dataset(datasetID):
    if not check_dataset_ownership(datasetID, session['useruuid']):
        flash("You don't have permission to delete this dataset.", "error")
        return redirect(url_for('DataManager'))
    success, message = SHARCFunctions.delete_dataset(datasetID)
    if success:
        SHARCFunctions.add_new_log(str(uuid.uuid1()), datetime.now(),session["useruuid"],"User Deleted Dataset",result_text=message)
        flash("Dataset deleted successfully!", "success")
    else:
        flash(f"Error deleting dataset: {message}", "error")
    return redirect(url_for('DataManager'))


######################
# Expedition Editor Page #
######################
@application.route('/expeditioneditor/<expedition>')
@login_required
@roles_required('Researcher')
def ExpeditionEditor(expedition):
    # If the user has clicked the new button they will come here
    if expedition == "new":
        # Generate a new UUID for the expedition
        newexpeditionuuid = str(uuid.uuid1())
        # Add the new expedition
        success, message = SHARCFunctions.add_new_expedition(newexpeditionuuid,"New Expedition")
       
        if not success:
            flash(f"Error creating new editor: {message}", "error")
            return redirect(url_for('home'))
        # Add the expedition to the user
        success, message = SHARCFunctions.add_user_to_expedition(session["useruuid"],newexpeditionuuid)
        if not success:
            flash(f"Error associating expedition with user: {message}", "error")
            return redirect(url_for('home'))

        SHARCFunctions.add_new_log(str(uuid.uuid1()), datetime.now(),session["useruuid"],"User Created New Expedition",result_text=message)
        return redirect(url_for('ExpeditionEditor', expedition=newexpeditionuuid))
    # Otherwise for existing sensors, proceed as before
    try:
        if expedition == "view":
            temp_results = SHARCFunctions.get_expeditions(user_uuid=session.get("useruuid"))
            if len(temp_results):
                expedition = temp_results[0].UUID 
            
        result = SHARCFunctions.get_expedition(expedition)

    except IndexError:

        flash("Expedition not found or you don't have permission to access it.", "error")
        return redirect(url_for('Home'))
    users = SHARCFunctions.getusers()
    expeditions = SHARCFunctions.get_expeditions(session["useruuid"])
    datasources = SHARCFunctions.getdatasources(session["useruuid"])
    return render_template('ExpeditionManager.html',
                           Logged_in=session.get('logged_in'),
                           Username=session.get('username'),
                           expedition=result,
                           expeditions = expeditions,
                           all_users=users,
                           datasources = datasources)

######################
# Expedition Viewer Page #
######################
@application.route('/expedition/<expedition>')
def ExpeditionViewer(expedition):
    try:
        if expedition == "view":
            temp_results = SHARCFunctions.get_expeditions()
            if len(temp_results):
                expedition = temp_results[0].UUID 
            
        result = SHARCFunctions.get_expedition(expedition)
    except IndexError:
        flash("Expedition not found or you don't have permission to access it.", "error")
        return redirect(url_for('Home'))
    expeditions = SHARCFunctions.get_expeditions()

    return render_template('ExpeditionViewer.html',
                           Logged_in=session.get('logged_in'),
                           Username=session.get('username'),
                           expeditions=expeditions,
                           expedition=result)



############################
# Datasource Deleter Route #
############################
@application.route('/datasourceeditor/<datasourceID>/delete')
@login_required
@roles_required('Researcher')
def delete_datasource(datasourceID):
    if not check_datasource_ownership(datasourceID, session['useruuid']):
        flash("You don't have permission to delete this datasource.", "error")
        return redirect(url_for('DatasourceAdmin'))

    success, message = SHARCFunctions.delete_datasource(datasourceID)
    if success:
        flash("Datasource deleted successfully!", "success")
        SHARCFunctions.add_new_log(str(uuid.uuid1()), datetime.now(),session["useruuid"],"User Deleted Datasource",result_text=message)
    else:
        flash(f"Error deleting datasource: {message}", "error")
    return redirect(url_for('DatasourceAdmin'))


############################
# Datasource Image Getter  #
############################
@application.route('/api/datasource/<datasourceUUID>/image', methods=['GET'])
def get_datasource_image(datasourceUUID):
    sensors = SHARCFunctions.getdatasources(datasourceuuid=datasourceUUID)
    if len(sensors) == 1:
        sensor = sensors[0]
    else:
        abort(404)
    # Get the image filename
    image_filename = sensor['Image']
    if image_filename == None:
        image_path = os.path.join(application.config['UPLOAD_FOLDER'],'ReadOnly')
        image_filename = 'sensor.png'
    else:
        # Construct the full path to the image file
        image_path = os.path.join(application.config['UPLOAD_FOLDER'])
    # Check if the file exists
    if not os.path.isfile(os.path.join(image_path,image_filename)):
        abort(404)  # Not found if the file doesn't exist
    # Send the file from the directory
    return send_from_directory(image_path, image_filename)

############################################
############################################
############################################
###             API Routing              ###
############################################
############################################
############################################
from AppAPI import api_bp
application.register_blueprint(api_bp, url_prefix='/api')



############################################
############################################
############################################
###          Program Functions           ###
############################################
############################################
############################################    
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
    return os.path.join(application.config['UPLOAD_FOLDER'], 'Datasets', dataset_id, filename)

############################################
############################################
############################################
###         Database Functions           ###
############################################
############################################
############################################

# In SHARCFunctions.py

############################################
############################################
############################################
###           End of Program             ###
############################################
############################################
############################################
if __name__ == '__main__':
    if DEBUG:
        application.run(host= '0.0.0.0',port=8000,debug=True)
    else:
        application.run() # no webserver - runs from gunicorn and nginx

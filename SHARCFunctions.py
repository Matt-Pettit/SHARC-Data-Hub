from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey, DateTime, Text, Table
from sqlalchemy.orm import relationship, sessionmaker, joinedload,declarative_base
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash

import datetime
Base = declarative_base()


data_source_dataset = Table('DataSourceDataset', Base.metadata,
    Column('DataSourceUUID', String, ForeignKey('DataSources.UUID'), primary_key=True),
    Column('DataSetUUID', String, ForeignKey('DataSets.UUID'), primary_key=True)
)
# Define Users table
class User(Base):
    __tablename__ = 'Users'
    UUID = Column(String, primary_key=True)
    UserName = Column(String, nullable=False)
    Password = Column(String, nullable=False)
    Salt = Column(String, nullable=False)
    Role = Column(String, nullable=False)
    data_sources = relationship("UserDataSource", back_populates="user")
    expeditions = relationship("ExpeditionUser", back_populates="user")
    logs = relationship("Log", back_populates="user")

class DataSource(Base):
    __tablename__ = 'DataSources'
    UUID = Column(String, primary_key=True)
    Name = Column(String, nullable=False)
    Description = Column(String)
    OnMap = Column(Boolean, nullable=False)
    Communicable = Column(Boolean, nullable=False)
    AdminApproved = Column(Boolean, nullable=False)
    DateCreated = Column(DateTime, nullable=False)
    Image = Column(String)
    locations = relationship("DataSourceLocation", back_populates="data_source")
    datasets = relationship("DataSet", secondary=data_source_dataset, back_populates="data_sources")
    sensors = relationship("DataSourceSensor", back_populates="data_source")
    users = relationship("UserDataSource", back_populates="data_source")
    expeditions = relationship("ExpeditionDataSource", back_populates="data_source")

class DataSourceLocation(Base):
    __tablename__ = 'DataSourceLocations'
    DataSourceUUID = Column(String, ForeignKey('DataSources.UUID'), primary_key=True)
    Location = Column(String, primary_key=True)
    DateTime = Column(DateTime, primary_key=True)
    Comment = Column(String)
    DeviceState = Column(String)
    data_source = relationship("DataSource", back_populates="locations")

class DataSourceSensor(Base):
    __tablename__ = 'DataSourceSensors'
    DataSourceUUID = Column(String, ForeignKey('DataSources.UUID'), primary_key=True)
    Sensor = Column(String, primary_key=True)
    data_source = relationship("DataSource", back_populates="sensors")

class DataSet(Base):
    __tablename__ = 'DataSets'
    UUID = Column(String, primary_key=True)
    Name = Column(String, nullable=False)
    Description = Column(String)
    Metadata = Column(String)
    FinishedProcessing = Column(Boolean, nullable=False)
    AdminApproved = Column(Boolean, nullable=False)
    DateAdded = Column(DateTime, nullable=False)
    data_sources = relationship("DataSource", secondary=data_source_dataset, back_populates="datasets")
    files = relationship("DataSetsFile", back_populates="data_set")

class DataSetsFile(Base):
    __tablename__ = 'DataSetsFiles'
    Dataset = Column(String, ForeignKey('DataSets.UUID'), primary_key=True)
    Filename = Column(String, nullable=False, primary_key=True)
    data_set = relationship("DataSet", back_populates="files")


class UserDataSource(Base):
    __tablename__ = 'UsersDataSources'
    UserUUID = Column(String, ForeignKey('Users.UUID'), primary_key=True)
    DataSourceUUID = Column(String, ForeignKey('DataSources.UUID'), primary_key=True)
    user = relationship("User", back_populates="data_sources")
    data_source = relationship("DataSource", back_populates="users")

class Expedition(Base):
    __tablename__ = 'Expeditions'
    UUID = Column(String, primary_key=True)
    Name = Column(String, nullable=False)
    Description = Column(Text)
    StartDate = Column(DateTime, nullable=False)
    EndDate = Column(DateTime)
    users = relationship("ExpeditionUser", back_populates="expedition")
    data_sources = relationship("ExpeditionDataSource", back_populates="expedition")

# New ExpeditionUser entity for many-to-many relationship
class ExpeditionUser(Base):
    __tablename__ = 'ExpeditionUsers'
    ExpeditionUUID = Column(String, ForeignKey('Expeditions.UUID'), primary_key=True)
    UserUUID = Column(String, ForeignKey('Users.UUID'), primary_key=True)
    expedition = relationship("Expedition", back_populates="users")
    user = relationship("User", back_populates="expeditions")

# New ExpeditionDataSource entity for many-to-many relationship
class ExpeditionDataSource(Base):
    __tablename__ = 'ExpeditionDataSources'
    ExpeditionUUID = Column(String, ForeignKey('Expeditions.UUID'), primary_key=True)
    DataSourceUUID = Column(String, ForeignKey('DataSources.UUID'), primary_key=True)
    expedition = relationship("Expedition", back_populates="data_sources")
    data_source = relationship("DataSource", back_populates="expeditions")

# New Log entity
class Log(Base):
    __tablename__ = 'Logs'
    UUID = Column(String, primary_key=True)
    Time = Column(DateTime, nullable=False)
    UserUUID = Column(String, ForeignKey('Users.UUID'))
    Description = Column(Text, nullable=False)
    ResultCode = Column(String)
    ResultText = Column(Text)
    user = relationship("User", back_populates="logs")

DATABASE_URL = "sqlite:///Database/combined_data.db"
engine = create_engine(DATABASE_URL, echo=False)
# Create all tables
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()




def authenticate_user(username,password):
    session = Session()
    # Retrieve the user from the database
    user = session.query(User).filter_by(UserName=username).first()
    if user:
        # Check the password
        session.close()
        return (check_password_hash(user.Password,password))
        #return (user.Password == password)
    else:
        # User not found
        session.close()
        return (False)

def getuuid_from_user(username):
    session = Session()
    # Retrieve the user from the database
    user = session.query(User).filter_by(UserName=username).first()
    
    if user:
        # Check the password
        session.close()
        return user.UUID
    else:
        # User not found
        session.close()
        return ("")

##################################
#        CREATER FUNCTIONS       #
##################################
def add_new_user(uuid, username, password, salt, role):
    session = Session()
    try:
        new_user = User(
            UUID=uuid,
            UserName=username,
            Password=password,
            Salt=salt,
            Role=role
        )
        session.add(new_user)
        session.commit()
        session.close()
        return True, "User added successfully"
    except IntegrityError:
        session.rollback()
        session.close()
        return False, "User with this UUID or username already exists"
    except Exception as e:
        session.rollback()
        session.close()
        return False, f"Error adding user: {str(e)}"

def add_new_dataset(uuid, name, description=None, metadata=None, 
                    finished_processing=False, admin_approved=False, date_added=None):
    session = Session()
    try:
        new_dataset = DataSet(
            UUID=uuid,
            Name=name,
            Description=description,
            Metadata=metadata,
            FinishedProcessing=finished_processing,
            AdminApproved=admin_approved,
            DateAdded=date_added or datetime.datetime.now()
        )
        session.add(new_dataset)
        session.commit()
        session.close()
        return True, "Dataset added successfully"
    except IntegrityError:
        session.rollback()
        session.close()
        return False, "Dataset with this UUID already exists"
    except Exception as e:
        session.rollback()
        session.close()
        return False, f"Error adding dataset: {str(e)}"


def add_new_datasource(uuid, name, description=None, on_map=False,
                       communicable=False, admin_approved=False, date_created=None,
                       image=None):
    session = Session()
    try:
        new_datasource = DataSource(
            UUID=uuid,
            Name=name,
            Description=description,
            OnMap=on_map,
            Communicable=communicable,
            AdminApproved=admin_approved,
            DateCreated=date_created or datetime.datetime.now(),
            Image=image
        )
        session.add(new_datasource)
        session.commit()
        session.close()
        return True, "DataSource added successfully"
    except IntegrityError:
        session.rollback()
        session.close()
        return False, "DataSource with this UUID already exists"
    except Exception as e:
        session.rollback()
        session.close()
        return False, f"Error adding datasource: {str(e)}"

##################################
#        UPDATER FUNCTIONS       #
##################################
def update_dataset(uuid, name=None, description=None, metadata=None, 
                   finished_processing=None, admin_approved=None, date_added=None):
    session = Session()
    try:
        dataset = session.query(DataSet).filter_by(UUID=uuid).one()
        if name is not None:
            dataset.Name = name
        if description is not None:
            dataset.Description = description
        if metadata is not None:
            dataset.Metadata = metadata
        if finished_processing is not None:
            dataset.FinishedProcessing = finished_processing
        if admin_approved is not None:
            dataset.AdminApproved = admin_approved
        if date_added is not None:
            dataset.DateAdded = date_added
        
        session.commit()
        session.close()
        return True, "Dataset updated successfully"
    except NoResultFound:
        session.close()
        return False, "Dataset not found"
    except Exception as e:
        session.rollback()
        session.close()
        return False, f"Error updating dataset: {str(e)}"

def update_datasource(uuid, name=None, description=None, on_map=None,
                      communicable=None, admin_approved=None, date_created=None,
                      image=None):
    session = Session()
    try:
        datasource = session.query(DataSource).filter_by(UUID=uuid).one()
        
        if name is not None:
            datasource.Name = name
        if description is not None:
            datasource.Description = description
        if on_map is not None:
            datasource.OnMap = on_map
        if communicable is not None:
            datasource.Communicable = communicable
        if admin_approved is not None:
            datasource.AdminApproved = admin_approved
        if date_created is not None:
            datasource.DateCreated = date_created
        if image is not None:
            datasource.Image = image
        
        session.commit()
        session.close()
        return True, "DataSource updated successfully"
    except NoResultFound:
        session.close()
        return False, "DataSource not found"
    except Exception as e:
        session.rollback()
        session.close()
        return False, f"Error updating datasource: {str(e)}"

def update_user(uuid, username=None, password=None, salt=None, role=None):
    print("Updating User")
    session = Session()
    try:
        user = session.query(User).filter_by(UUID=uuid).one()
        
        if username is not None:
            user.UserName = username
        if password is not None:
            user.Password = password
        if salt is not None:
            user.Salt = salt
        if role is not None:
            user.Role = role
        
        session.commit()
        session.close()
        return True, "User updated successfully"
    except NoResultFound:
        session.close()
        return False, "User not found"
    except Exception as e:
        session.rollback()
        session.close()
        return False, f"Error updating user: {str(e)}"


##################################
#         file to dataset        #
##################################
def add_file_to_dataset(dataset_uuid, filename):
    session = Session()
    try:
        new_file = DataSetsFile(Dataset=dataset_uuid, Filename=filename)
        session.add(new_file)
        session.commit()
        session.close()
        return True, f"File '{filename}' added to dataset '{dataset_uuid}'"
    except IntegrityError:
        session.rollback()
        session.close()
        return False, f"File '{filename}' already exists in dataset '{dataset_uuid}'"
    except Exception as e:
        session.rollback()
        session.close()
        return False, f"Error adding file to dataset: {str(e)}"

def remove_file_from_dataset(dataset_uuid, filename):
    session = Session()
    try:
        file = session.query(DataSetsFile).filter_by(Dataset=dataset_uuid, Filename=filename).one()
        print(file.Filename)
        session.delete(file)
        session.commit()
        session.close()
        return True, f"File '{filename}' removed from dataset '{dataset_uuid}'"
    except NoResultFound:
        session.close()
        return False, f"File '{filename}' not found in dataset '{dataset_uuid}'"
    except Exception as e:
        session.rollback()
        session.close()
        return False, f"Error removing file from dataset: {str(e)}"


##################################
#         datasource to user     #
##################################
def add_datasource_to_user(user_uuid, datasource_uuid):
    session = Session()
    try:
        new_user_datasource = UserDataSource(UserUUID=user_uuid, DataSourceUUID=datasource_uuid)
        session.add(new_user_datasource)
        session.commit()
        session.close()
        return True, f"DataSource '{datasource_uuid}' added to user '{user_uuid}'"
    except IntegrityError:
        session.rollback()
        session.close()
        return False, f"DataSource '{datasource_uuid}' already associated with user '{user_uuid}'"
    except Exception as e:
        session.rollback()
        session.close()
        return False, f"Error adding datasource to user: {str(e)}"

def remove_datasource_from_user(user_uuid, datasource_uuid):
    session = Session()
    try:
        user_datasource = session.query(UserDataSource).filter_by(UserUUID=user_uuid, DataSourceUUID=datasource_uuid).one()
        session.delete(user_datasource)
        session.commit()
        session.close()
        return True, f"DataSource '{datasource_uuid}' removed from user '{user_uuid}'"
    except NoResultFound:
        session.close()
        return False, f"DataSource '{datasource_uuid}' not associated with user '{user_uuid}'"
    except Exception as e:
        session.rollback()
        session.close()
        return False, f"Error removing datasource from user: {str(e)}"


##################################
#      dataset to datasource     #
##################################
def add_dataset_to_datasource(dataset_uuid, datasource_uuid):
    session = Session()
    try:
        dataset = session.query(DataSet).filter_by(UUID=dataset_uuid).one()
        datasource = session.query(DataSource).filter_by(UUID=datasource_uuid).one()
        dataset.data_sources.append(datasource)
        session.commit()
        session.close()
        return True, f"Dataset '{dataset_uuid}' added to DataSource '{datasource_uuid}'"
    except NoResultFound:
        session.close()
        return False, f"Dataset '{dataset_uuid}' or DataSource '{datasource_uuid}' not found"
    except Exception as e:
        session.rollback()
        session.close()
        return False, f"Error adding dataset to datasource: {str(e)}"

def remove_dataset_from_datasource(dataset_uuid, datasource_uuid):
    session = Session()
    try:
        dataset = session.query(DataSet).filter_by(UUID=dataset_uuid).one()
        datasource = session.query(DataSource).filter_by(UUID=datasource_uuid).one()
        dataset.data_sources.remove(datasource)
        session.commit()
        session.close()
        return True, f"Dataset '{dataset_uuid}' removed from DataSource '{datasource_uuid}'"
    except NoResultFound:
        session.close()
        return False, f"Dataset '{dataset_uuid}' or DataSource '{datasource_uuid}' not found"
    except Exception as e:
        session.rollback()
        session.close()
        return False, f"Error removing dataset from datasource: {str(e)}"


##################################
#     location to datasource     #
##################################
def add_location_to_datasource(datasource_uuid, location, date_time, comment, devicestate):
    session = Session()
    try:
        new_location = DataSourceLocation(DataSourceUUID=datasource_uuid, Location=location, DateTime=date_time, Comment=comment, DeviceState=devicestate)
        session.add(new_location)
        session.commit()
        session.close()
        return True, f"Location '{location}' added to DataSource '{datasource_uuid}'"
    except IntegrityError:
        session.rollback()
        session.close()
        return False, f"Location '{location}' at '{date_time}' already exists for DataSource '{datasource_uuid}'"
    except Exception as e:
        session.rollback()
        session.close()
        return False, f"Error adding location to datasource: {str(e)}"

def remove_location_from_datasource(datasource_uuid, location, date_time):
    session = Session()
    try:
        location = session.query(DataSourceLocation).filter_by(
            DataSourceUUID=datasource_uuid, Location=location, DateTime=date_time).one()
        session.delete(location)
        session.commit()
        session.close()
        return True, f"Location '{location}' at '{date_time}' removed from DataSource '{datasource_uuid}'"
    except NoResultFound:
        session.close()
        return False, f"Location '{location}' at '{date_time}' not found for DataSource '{datasource_uuid}'"
    except Exception as e:
        session.rollback()
        session.close()
        return False, f"Error removing location from datasource: {str(e)}"


def update_location_from_datasource(datasource_uuid, location, date_time, comment=None, devicestate=None):
    session = Session()
    try:
        # Find the existing location record
        location_record = session.query(DataSourceLocation).filter_by(
            DataSourceUUID=datasource_uuid,
            Location=location,
            DateTime=date_time
        ).one()

        # Update the fields if new values are provided
        if comment is not None:
            location_record.Comment = comment
        if devicestate is not None:
            location_record.DeviceState = devicestate

        session.commit()
        session.close()
        return True, f"Location '{location}' at '{date_time}' updated for DataSource '{datasource_uuid}'"
    except NoResultFound:
        session.close()
        return False, f"Location '{location}' at '{date_time}' not found for DataSource '{datasource_uuid}'"
    except Exception as e:
        session.rollback()
        session.close()
        return False, f"Error updating location for datasource: {str(e)}"


##################################
#     sensor to datasource       #
##################################
def add_sensor_to_datasource(datasource_uuid, sensor):
    session = Session()
    try:
        new_sensor = DataSourceSensor(DataSourceUUID=datasource_uuid, Sensor=sensor)
        session.add(new_sensor)
        session.commit()
        session.close()
        return True, f"Sensor '{sensor}' added to DataSource '{datasource_uuid}'"
    except IntegrityError:
        session.rollback()
        session.close()
        return False, f"Sensor '{sensor}' already exists for DataSource '{datasource_uuid}'"
    except Exception as e:
        session.rollback()
        session.close()
        return False, f"Error adding sensor to datasource: {str(e)}"

def remove_sensor_from_datasource(datasource_uuid, sensor):
    session = Session()
    try:
        sensor = session.query(DataSourceSensor).filter_by(DataSourceUUID=datasource_uuid, Sensor=sensor).one()
        session.delete(sensor)
        session.commit()
        session.close()
        return True, f"Sensor '{sensor}' removed from DataSource '{datasource_uuid}'"
    except NoResultFound:
        session.close()
        return False, f"Sensor '{sensor}' not found for DataSource '{datasource_uuid}'"
    except Exception as e:
        session.rollback()
        session.close()
        return False, f"Error removing sensor from datasource: {str(e)}"





###############################
#    Page Function Wrappers   #
###############################
def getdatasets(useruuid=None, datasetuuid=None):
    session = Session()
    query = session.query(DataSet).options(
        joinedload(DataSet.data_sources),
        joinedload(DataSet.files)
    )

    if useruuid is not None:
        query = query.join(DataSet.data_sources).join(DataSource.users).filter(UserDataSource.UserUUID == useruuid)
    if datasetuuid is not None:
        query = query.filter(DataSet.UUID == datasetuuid)

    all_datasets = query.all()

    results = []
    for dataset in all_datasets:
        dataset_dict = {
            'UUID': dataset.UUID,
            'Name': dataset.Name,
            'Description': dataset.Description,
            'Metadata': dataset.Metadata,
            'AdminApproved': dataset.AdminApproved,
            'FinishedProcessing': dataset.FinishedProcessing,
            'DateAdded': dataset.DateAdded,
            'Files': [(file.Dataset, file.Filename) for file in dataset.files],
            'DataSources': [{'UUID': ds.UUID, 'Name': ds.Name} for ds in dataset.data_sources]
        }
        results.append(dataset_dict)
    
    session.close()
    return results


def getdatasources(useruuid=None, datasourceuuid=None):
    session = Session()
    
    # Specific Searches
    if useruuid is None:
        all_datasources = session.query(DataSource).all()
    elif useruuid is not None:
        all_datasources = session.query(DataSource).join(UserDataSource).filter(UserDataSource.UserUUID == useruuid).all()


    #elif datasourceuuid is not None:
    #    all_datasources = session.query(DataSource).filter(DataSource.UUID == datasourceuuid).all()
    
    # Create Dictionary List 
    results = []
    for datasource in all_datasources:
        if datasourceuuid is not None:
            if datasource.UUID != datasourceuuid:
                continue
        datasource_dict = {
            'UUID': datasource.UUID,
            'Name': datasource.Name,
            'Description': datasource.Description,
            'OnMap': datasource.OnMap,
            'Communicable': datasource.Communicable,
            'AdminApproved': datasource.AdminApproved,
            'DateCreated': datasource.DateCreated,
            'Image': datasource.Image,
            'Locations': [{'Location': loc.Location, 'DateTime': loc.DateTime, 'Comment': loc.Comment, 'DeviceState' : loc.DeviceState} for loc in datasource.locations],
            'Sensors': [sensor.Sensor for sensor in datasource.sensors],
            'Datasets': [{'UUID': dataset.UUID, 'Name': dataset.Name} for dataset in datasource.datasets],
            'Users': [{'UUID': user.UserUUID,'Name' : user.user.UserName} for user in datasource.users]
        }
        results.append(datasource_dict)
    session.close()
    return results

def getusers(useruuid=None, role=None):
    session = Session()
    
    # Start with a base query
    query = session.query(User)
    
    # Apply filters if provided
    if useruuid is not None:
        query = query.filter(User.UUID == useruuid)
    if role is not None:
        query = query.filter(User.Role == role)
    
    # Execute the query
    all_users = query.all()
    
    # Create Dictionary List 
    results = []
    for user in all_users:
        user_dict = {
            'UUID': user.UUID,
            'UserName': user.UserName,
            'Role': user.Role,
            'DataSources': [{'UUID': datasource.DataSourceUUID} for datasource in user.data_sources]
        }
        results.append(user_dict)
    
    session.close()
    return results


##################################
#        DELETE FUNCTIONS        #
##################################
def delete_dataset(dataset_uuid):
    session = Session()
    try:
        dataset = session.query(DataSet).filter_by(UUID=dataset_uuid).one()

        # Remove associations with data sources
        dataset.data_sources = []

        # Delete associated files
        for file in dataset.files:
            session.delete(file)

        # Delete the dataset
        session.delete(dataset)

        session.commit()
        session.close()
        return True, "Dataset deleted successfully"
    except NoResultFound:
        session.close()
        return False, "Dataset not found"
    except Exception as e:
        session.rollback()
        session.close()
        print(f"Error deleting dataset: {e}")
        return False, f"Error deleting dataset: {str(e)}"

def delete_datasource(datasource_uuid):
    session = Session()
    try:
        # Delete all UserDataSource entries for this datasource
        session.query(UserDataSource).filter_by(DataSourceUUID=datasource_uuid).delete(synchronize_session='fetch')
        # Delete ExpeditionDataSource entries
        session.query(ExpeditionDataSource).filter_by(DataSourceUUID=datasource_uuid).delete(synchronize_session='fetch')

        # Delete associated sensors
        session.query(DataSourceSensor).filter_by(DataSourceUUID=datasource_uuid).delete(synchronize_session='fetch')
        # Remove relationships with datasets

        # Delete associated locations
        session.query(DataSourceLocation).filter_by(DataSourceUUID=datasource_uuid).delete(synchronize_session='fetch')
        # Now fetch the datasource, need to update so that it is able to deleet
        datasource = session.query(DataSource).options(
            joinedload(DataSource.locations),
            joinedload(DataSource.sensors),
            joinedload(DataSource.datasets)
        ).filter_by(UUID=datasource_uuid).one()



        #datasource.datasets = []
        # Now delete the datasource
        session.delete(datasource)

        session.commit()
        session.close()
        return True, "DataSource deleted successfully"
    except NoResultFound:
        session.close()
        return False, "DataSource not found"
    except Exception as e:
        session.rollback()
        session.close()
        print(f"Error deleting datasource: {str(e)}")
        return False, f"Error deleting datasource: {str(e)}"


##################################
#        GETTER FUNCTIONS        #
##################################

def get_expedition(uuid):
    session = Session()
    try:
        expedition = (
        session.query(Expedition)
        .options(
            joinedload(Expedition.users)
            .joinedload(ExpeditionUser.user),
            joinedload(Expedition.data_sources)
            .joinedload(ExpeditionDataSource.data_source)
        )
        .filter_by(UUID=uuid)
        .one()
        )

        #expedition.users
        #print(expedition.users)
        session.close()
        return expedition
    except NoResultFound:
        session.close()
        return None

def get_expeditions(user_uuid=None):
    session = Session()
    try:
        if user_uuid:
            expeditions = session.query(Expedition).join(ExpeditionUser).filter(ExpeditionUser.UserUUID == user_uuid).all()
        else:
            expeditions = session.query(Expedition).all()

        session.close()
        return expeditions
    except Exception as e:
        session.close()
        return []

# def get_expeditions_by_datasource(datasource_uuid):
#     session = Session()
#     try:
#         expeditions = session.query(Expedition).join(ExpeditionDataSource).filter(ExpeditionDataSource.DataSourceUUID == datasource_uuid).all()
#         session.close()
#         return expeditions
#     except Exception as e:
#         session.close()
#         return []

def get_logs(user_uuid=None):
    session = Session()
    try:
        query = session.query(Log).options(joinedload(Log.user))
        
        if user_uuid:
            logs = query.filter_by(UserUUID=user_uuid).all()
        else:
            logs = query.all()
        
        return logs
    except Exception as e:
        print(f"Error retrieving logs: {str(e)}")
        return []
    finally:
        session.close()

##################################
#        CREATER FUNCTIONS       #
##################################

def add_new_expedition(uuid, name, description=None, start_date=None, end_date=None):
    session = Session()
    try:
        new_expedition = Expedition(
            UUID=uuid,
            Name=name,
            Description=description,
            StartDate=start_date or datetime.datetime.now(),
            EndDate=end_date
        )
        session.add(new_expedition)
        session.commit()
        session.close()
        return True, "Expedition added successfully"
    except IntegrityError:
        session.rollback()
        session.close()
        return False, "Expedition with this UUID already exists"
    except Exception as e:
        session.rollback()
        session.close()
        return False, f"Error adding expedition: {str(e)}"

def add_new_log(uuid, time, user_uuid, description, result_code=None, result_text=None):
    session = Session()
    try:
        new_log = Log(
            UUID=uuid,
            Time=time,
            UserUUID=user_uuid,
            Description=description,
            ResultCode=result_code,
            ResultText=result_text
        )
        session.add(new_log)
        session.commit()
        session.close()
        return True, "Log added successfully"
    except IntegrityError:
        session.rollback()
        session.close()
        return False, "Log with this UUID already exists"
    except Exception as e:
        session.rollback()
        session.close()
        return False, f"Error adding log: {str(e)}"

##################################
#        UPDATER FUNCTIONS       #
##################################

def update_expedition(uuid, name=None, description=None, start_date=None, end_date=None):
    session = Session()
    try:
        expedition = session.query(Expedition).filter_by(UUID=uuid).one()
        if name is not None:
            expedition.Name = name
        if description is not None :
            expedition.Description = description
        if start_date is not None:
            expedition.StartDate = start_date
        if end_date is not None:
            expedition.EndDate = end_date
        
        session.commit()
        session.close()
        return True, "Expedition updated successfully"
    except NoResultFound:
        session.close()
        return False, "Expedition not found"
    except Exception as e:
        session.rollback()
        session.close()
        return False, f"Error updating expedition: {str(e)}"

##################################
#    RELATIONSHIP FUNCTIONS      #
##################################

def add_user_to_expedition(user_uuid, expedition_uuid):
    session = Session()
    try:
        new_expedition_user = ExpeditionUser(UserUUID=user_uuid, ExpeditionUUID=expedition_uuid)
        session.add(new_expedition_user)
        session.commit()
        session.close()
        return True, f"User '{user_uuid}' added to Expedition '{expedition_uuid}'"
    except IntegrityError:
        session.rollback()
        session.close()
        return False, f"User '{user_uuid}' is already associated with Expedition '{expedition_uuid}'"
    except Exception as e:
        session.rollback()
        session.close()
        return False, f"Error adding user to expedition: {str(e)}"

def remove_user_from_expedition(user_uuid, expedition_uuid):
    session = Session()
    try:
        expedition_user = session.query(ExpeditionUser).filter_by(UserUUID=user_uuid, ExpeditionUUID=expedition_uuid).one()
        session.delete(expedition_user)
        session.commit()
        session.close()
        return True, f"User '{user_uuid}' removed from Expedition '{expedition_uuid}'"
    except NoResultFound:
        session.close()
        return False, f"User '{user_uuid}' is not associated with Expedition '{expedition_uuid}'"
    except Exception as e:
        session.rollback()
        session.close()
        return False, f"Error removing user from expedition: {str(e)}"

def add_datasource_to_expedition(datasource_uuid, expedition_uuid):
    session = Session()
    try:
        new_expedition_datasource = ExpeditionDataSource(DataSourceUUID=datasource_uuid, ExpeditionUUID=expedition_uuid)
        session.add(new_expedition_datasource)
        session.commit()
        session.close()
        return True, f"DataSource '{datasource_uuid}' added to Expedition '{expedition_uuid}'"
    except IntegrityError:
        session.rollback()
        session.close()
        return False, f"DataSource '{datasource_uuid}' is already associated with Expedition '{expedition_uuid}'"
    except Exception as e:
        session.rollback()
        session.close()
        return False, f"Error adding datasource to expedition: {str(e)}"

def remove_datasource_from_expedition(datasource_uuid, expedition_uuid):
    session = Session()
    try:
        expedition_datasource = session.query(ExpeditionDataSource).filter_by(DataSourceUUID=datasource_uuid, ExpeditionUUID=expedition_uuid).one()
        session.delete(expedition_datasource)
        session.commit()
        session.close()
        return True, f"DataSource '{datasource_uuid}' removed from Expedition '{expedition_uuid}'"
    except NoResultFound:
        session.close()
        return False, f"DataSource '{datasource_uuid}' is not associated with Expedition '{expedition_uuid}'"
    except Exception as e:
        session.rollback()
        session.close()
        return False, f"Error removing datasource from expedition: {str(e)}"


def delete_expedition(expedition_uuid):
    session = Session()
    try:
        # First, delete all ExpeditionUser entries for this expedition
        session.query(ExpeditionUser).filter_by(ExpeditionUUID=expedition_uuid).delete(synchronize_session='fetch')
        
        # Delete ExpeditionDataSource entries
        session.query(ExpeditionDataSource).filter_by(ExpeditionUUID=expedition_uuid).delete(synchronize_session='fetch')

        # Now fetch the expedition
        expedition = session.query(Expedition).options(
            joinedload(Expedition.users),
            joinedload(Expedition.data_sources)
        ).filter_by(UUID=expedition_uuid).one()

        # Remove relationships with users and data sources
        expedition.users = []
        expedition.data_sources = []

        # Now delete the expedition itself
        session.delete(expedition)

        session.commit()
        session.close()
        return True, "Expedition deleted successfully"
    except NoResultFound:
        session.close()
        return False, "Expedition not found"
    except Exception as e:
        session.rollback()
        session.close()
        print(f"Error deleting expedition: {str(e)}")
        return False, f"Error deleting expedition: {str(e)}"
from sqlalchemy import create_engine, Column, String, Boolean, DateTime, ForeignKey, Integer, Text, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
import uuid
import hashlib
import os

Base = declarative_base()

# Many-to-many relationship table for DataSources and DataSets
data_source_dataset = Table('DataSourceDataset', Base.metadata,
    Column('DataSourceUUID', String, ForeignKey('DataSources.UUID'), primary_key=True),
    Column('DataSetUUID', String, ForeignKey('DataSets.UUID'), primary_key=True)
)

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

class ExpeditionUser(Base):
    __tablename__ = 'ExpeditionUsers'
    ExpeditionUUID = Column(String, ForeignKey('Expeditions.UUID'), primary_key=True)
    UserUUID = Column(String, ForeignKey('Users.UUID'), primary_key=True)
    expedition = relationship("Expedition", back_populates="users")
    user = relationship("User", back_populates="expeditions")

class ExpeditionDataSource(Base):
    __tablename__ = 'ExpeditionDataSources'
    ExpeditionUUID = Column(String, ForeignKey('Expeditions.UUID'), primary_key=True)
    DataSourceUUID = Column(String, ForeignKey('DataSources.UUID'), primary_key=True)
    expedition = relationship("Expedition", back_populates="data_sources")
    data_source = relationship("DataSource", back_populates="expeditions")

class Log(Base):
    __tablename__ = 'Logs'
    UUID = Column(String, primary_key=True)
    Time = Column(DateTime, nullable=False)
    UserUUID = Column(String, ForeignKey('Users.UUID'))
    Description = Column(Text, nullable=False)
    ResultCode = Column(String)
    ResultText = Column(Text)
    user = relationship("User", back_populates="logs")



# Create the database
DATABASE_URL = "sqlite:///combined_data.db"
engine = create_engine(DATABASE_URL, echo=False)

# Create all tables
Base.metadata.create_all(engine)

print("Database and tables created successfully.")


Base.metadata.create_all(engine)

# Create a session
Session = sessionmaker(bind=engine)
session = Session()

def create_fake_users():
    fake_users = [
        {"username": "Matt Pettit", "password": "scrypt:32768:8:1$IQ0E1kcYeIK2H3nr$3f6d035418ed291655d29a2e250e5bef9b305a0705a9ccc44859495b17ec9d541a815aca1bb2bbcdb27f177e80fdbbd581b197b87ec835ca5711f0bf1b5b13c4", "role": "Administrator"},
    ]

    for user_data in fake_users:
        # Generate a random salt
        salt = os.urandom(32).hex()
        
        # Hash the password with the salt
        hashed_password = hashlib.sha256((user_data["password"] + salt).encode()).hexdigest()
        
        # Create a new User instance
        new_user = User(
            UUID=str(uuid.uuid4()),
            UserName=user_data["username"],
            Password=user_data["password"],
            Salt='',
            Role=user_data["role"]
        )
        
        # Add the new user to the session
        session.add(new_user)
    
    # Commit the changes
    session.commit()
    print(f"{len(fake_users)} fake users added successfully.")

# Create fake users
create_fake_users()

print("Database and tables created successfully with fake users.")

# Close the session
session.close()
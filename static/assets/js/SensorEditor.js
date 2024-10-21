function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

function updateSensor() {
    const sensorName = document.getElementById('SensorNameInput').value;
    const sensorID = document.getElementById('sensorID').value;
    const sensorDescription = document.getElementById('SensorDescriptionInput').value;

    
    fetch('/api/datasource/update', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            sensorName: sensorName,
            sensorID: sensorID,
            sensorDescription: sensorDescription
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            //alert('Sensor information updated successfully!');
            Swal.fire({
                position: "top-middle",
                icon: "success",
                title: "Sensor information updated successfully!",
                showConfirmButton: false,
                timer: 1500
              });
        } else {
            //alert('Error updating sensor information.');
            Swal.fire({
                position: "top-middle",
                icon: "error",
                title: "Sensor information update failed",
                confirmButtonColor: '#00243a',
                showConfirmButton: true
              });
        }
    })
    .catch(error => {
        console.error('Error:', error);
        //alert('An error occurred while updating sensor information.');
        Swal.fire({
            position: "top-middle",
            icon: "error",
            title: "Sensor information update failed",
            confirmButtonColor: '#00243a',
            showConfirmButton: true

          });
    });
}

function addSensor() {
    const sensorName = document.getElementById('AddSensorInput').value;
    const sensorID = document.getElementById('sensorID').value;
    if (!sensorName) {
        //alert('Please enter a sensor name.');
        Swal.fire({
            position: "top-middle",
            icon: "warning",
            title: "Please enter a sensor name.",
            showConfirmButton: false,
            timer: 1500
          });
        return;
    }

    fetch('/api/datasource/add_sensor', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            sensorID: sensorID,
            sensorName: sensorName
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            //alert('Sensor added successfully!');
            Swal.fire({
                position: "top-middle",
                icon: "success",
                title: "Sensor added successfully!",
                showConfirmButton: false,
                timer: 1500
              })
            document.getElementById('AddSensorInput').value = ''; // Clear the input field
            //sleep(5000);
            location.reload(true);
        } else {
            //alert('Error adding sensor: ' + data.message);
            Swal.fire({
                position: "top-middle",
                icon: "error",
                title: "Sensor adding failed!",
                confirmButtonColor: '#00243a',
                showConfirmButton: true
              });
            
        }
    })
    .catch(error => {
        console.error('Error:', error);
        //alert('An error occurred while adding the sensor.');
        Swal.fire({
            position: "top-middle",
            icon: "error",
            title: "Sensor adding failed!",
            confirmButtonColor: '#00243a',
            showConfirmButton: true
          });
    });
}

function uploadImage() {
    const fileInput = document.getElementById('SensorImagePicker');
    const sensorID = document.getElementById('sensorID').value;

    const file = fileInput.files[0];

    if (!file) {
        //alert('Please select an image to upload.');
        Swal.fire({
            position: "top-middle",
            icon: "warning",
            title: "Please select an image to upload.",
            showConfirmButton: false,
            timer: 1500
          })
        return;
    }

    const formData = new FormData();
    formData.append('image', file);
    formData.append('sensorID', sensorID);
    fetch('/api/datasource/upload_image', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {

            // Optionally, you can update the UI to show the uploaded image
            location.reload(true);
        } else {
            Swal.fire({
                position: "top-middle",
                icon: "error",
                title: "Error uploading image!",
                showConfirmButton: true,
                confirmButtonColor: '#00243a',
              })
            console.log('Error uploading image: ' + data.message);
        }
    })
    .catch(error => {
        Swal.fire({
            position: "top-middle",
            icon: "error",
            title: "Error uploading image!",
            showConfirmButton: true,
            confirmButtonColor: '#00243a',
          })
        console.log('Error uploading image: ' + data.message);
        // console.error('Error:', error);
        // alert('An error occurred while uploading the image.');
    });
}

function addLocationData() {
    const dateTime = document.getElementById('LocationDateTimeInput').value;
    const location = document.getElementById('LocationLocationInput').value;
    const comment = document.getElementById('LocationCommentInput').value;
    const sensorID = document.getElementById('sensorID').value;
    const devicestate = document.getElementById('DeviceState').value;


    if (!dateTime || !location) {
        //alert('Please enter both Date Time and Location.');
        Swal.fire({
            position: "top-middle",
            icon: "warning",
            title: "Please enter both Date Time and Location.",
            showConfirmButton: false,
            timer : 1500
        })
        return;
    }

    fetch('/api/datasource/add_location', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            dateTime: dateTime,
            location: location,
            sensorID: sensorID,
            comment: comment,
            devicestate: devicestate
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
           // alert('Location data added successfully!');
            document.getElementById('LocationDateTimeInput').value = ''; // Clear the input fields
            document.getElementById('LocationLocationInput').value = '';
            document.getElementById('LocationCommentInput').value = '';
            window.location.reload(true);
        } else {
            //alert('Error adding location data: ' + data.message);
            console.log(data.message);
            Swal.fire({
                position: "top-middle",
                icon: "error",
                title: "Error adding location data!",
                showConfirmButton: true,
                confirmButtonColor: '#00243a',
            })
        }
    })
    .catch(error => {
        console.error('Error:', error);
        //alert('An error occurred while adding location data.');
        Swal.fire({
            position: "top-middle",
            icon: "error",
            title: "Error adding location data!",
            showConfirmButton: true,
            confirmButtonColor: '#00243a',
        })
    });
}

document.addEventListener('DOMContentLoaded', function() {
    const locationDataTable = document.getElementById('locationDataTable');
    const saveLocationsBtn = document.getElementById('SaveLocationsBtn');

    // Add event listener for device state changes
    locationDataTable.addEventListener('change', function(event) {
        if (event.target.classList.contains('device-state-select')) {
            updatePreviousStates(event.target);
        }
    });

    // Add event listener for saving location data changes
    saveLocationsBtn.addEventListener('click', saveLocationDataChanges);
});

function updatePreviousStates(changedSelect) {
    const newState = changedSelect.value;
    let currentRow = changedSelect.closest('tr');

    while (currentRow = currentRow.previousElementSibling) {
        const stateSelect = currentRow.querySelector('.device-state-select');
        stateSelect.value = newState;
    }
}

function saveLocationDataChanges() {
    const sensorID = document.getElementById('sensorID').value;
    console.log(sensorID)
    const rows = document.querySelectorAll('#locationDataTable tbody tr');
    const updatedLocations = [];

    rows.forEach(row => {
        updatedLocations.push({
            DateTime: row.cells[0].textContent,
            Location: row.cells[1].textContent,
            Comment: row.cells[2].textContent,
            DeviceState: row.querySelector('.device-state-select').value
        });
    });

    fetch('/api/datasource/update_locations', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            sensorID: sensorID,
            locations: updatedLocations
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            //alert('Location data updated successfully!');
            location.reload(true);
        } else {
            //alert('Error updating location data: ' + data.message);
            Swal.fire({
                position: "top-middle",
                icon: "error",
                title: "Error updating location data!",
                showConfirmButton: true,
                confirmButtonColor: '#00243a',
            })
        }
    })
    .catch(error => {
        console.error('Error:', error);
        //alert('An error occurred while updating location data.');
        Swal.fire({
            position: "top-middle",
            icon: "error",
            title: "Error updating location data!",
            showConfirmButton: true,
            confirmButtonColor: '#00243a',
        })
    });
}


// Function to remove a sensor
function removeSensor(sensorName) {
    const sensorID = document.getElementById('sensorID').value;
    fetch('/api/datasource/remove_sensor', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            sensorID: sensorID,
            sensorName: sensorName
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            //alert('Sensor removed successfully!');
            location.reload(true);

        } else {
            //alert('Error removing sensor: ' + data.message);
            Swal.fire({
                position: "top-middle",
                icon: "error",
                title: "Error removing sensor!",
                showConfirmButton: true,
                confirmButtonColor: '#00243a',
              })
            console.log('Error removing sensor: ' + data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        Swal.fire({
            position: "top-middle",
            icon: "error",
            title: "Error removing sensor!",
            showConfirmButton: true,
            confirmButtonColor: '#00243a',
          })
    });
}

// Function to remove location data
function removeLocationData(dateTime, Location) {
    const sensorID = document.getElementById('sensorID').value;
    fetch('/api/datasource/remove_location', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            sensorID: sensorID,
            dateTime: dateTime,
            location: Location
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            //alert('Location data removed successfully!');
            location.reload(true);
        } else {
            alert('Error removing location data: ' + data.message);
            Swal.fire({
                position: "top-middle",
                icon: "error",
                title: "Error removing location data!",
                showConfirmButton: true,
                confirmButtonColor: '#00243a',
            })
        }
    })
    .catch(error => {
        console.error('Error:', error);
        Swal.fire({
            position: "top-middle",
            icon: "error",
            title: "Error removing location data!",
            showConfirmButton: true,
            confirmButtonColor: '#00243a',
        })
    });
}

function addUser() {
    const sensorID = document.getElementById('sensorID').value;

    const userSelect = document.getElementById('AddUserSelect');
    const userId = userSelect.value;
    const userName = userSelect.options[userSelect.selectedIndex].text;

    if (!userId) {
        Swal.fire({
            position: "top-middle",
            icon: "error",
            title: "Select a user to add.",
            showConfirmButton: true,
            confirmButtonColor: '#00243a'
          });
        return;
    }

    fetch('/api/datasource/add_user', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ sensorID: sensorID, userId: userId })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            Swal.fire({
                position: "top-middle",
                icon: "success",
                title: "User added successfully",
                showConfirmButton: false,
                timer : 1500
              });
              location.reload();
        } else {
            Swal.fire({
                position: "top-middle",
                icon: "error",
                title: "Error Adding User",
                text: data.message,
                showConfirmButton: true,
                confirmButtonColor: '#00243a'
              });
        }
    })
    .catch(error => {
        console.error('Error:', error);
        Swal.fire({
            position: "top-middle",
            icon: "error",
            title: "Error Adding User",
            text: error,
            showConfirmButton: true
          });
    });
}

function removeUser(userId) {
    const sensorID = document.getElementById('sensorID').value;

    Swal.fire({
        title: 'Are you sure?',
        text: "You are about to remove this user from the data source.",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#00243a',
        cancelButtonColor: '#d33',
        confirmButtonText: 'Yes, remove it!'
    }).then((result) => {
        if (result.isConfirmed) {
            fetch('/api/datasource/remove_user', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ sensorID: sensorID, userId: userId })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    Swal.fire({
                        position: "top-middle",
                        icon: "success",
                        title: "User removed successfully",
                        showConfirmButton: false,
                        timer : 1500
                      });
                    location.reload();
                } else {
                    Swal.fire({
                        position: "top-middle",
                        icon: "error",
                        title: "User could not be removed successfully",
                        text: data.message,
                        showConfirmButton: true,
                        confirmButtonColor: '#00243a'
                      });
                }
            })
            .catch(error => {
                console.error('Error:', error);
                Swal.fire({
                    position: "top-middle",
                    icon: "error",
                    title: "User could not be removed successfully",
                    text: error,
                    showConfirmButton: true,
                    confirmButtonColor: '#00243a'
                  });
            });
        }
    });
}
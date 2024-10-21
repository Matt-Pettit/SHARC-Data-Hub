
function uploadFiles() {
    const fileInput = document.getElementById('MultipleFileUpload');
    const datasetID = document.getElementById('datasetID').value;
    const files = fileInput.files;

    if (files.length === 0) {
        //alert('Please select one or more files to upload.');
        Swal.fire({
            position: "top-middle",
            icon: "warning",
            title: "Please select one or more files to upload.",
            showConfirmButton: false,
            timer: 1500
          });
        return;
    }

    const formData = new FormData();
    formData.append('datasetID', datasetID);
    for (let i = 0; i < files.length; i++) {
        formData.append('files', files[i]);
    }

    fetch('/api/dataset/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            Swal.fire({
                position: "top-middle",
                icon: "success",
                title: 'Successfully uploaded file(s)!',
                showConfirmButton: false,
                timer: 1500
              });
            fileInput.value = ''; 
        } else {
            Swal.fire({
                position: "top-middle",
                icon: "error",
                title: 'Error uploading files!',
                showConfirmButton: true,
                confirmButtonColor: '#00243a'
            });
        }
    })
    .catch(error => {
        console.error('Error:', error);
        //alert('An error occurred while uploading the files.');
        Swal.fire({
            position: "top-middle",
            icon: "error",
            title: 'Error uploading files!',
            showConfirmButton: true,
            confirmButtonColor: '#00243a'
        });
    });
}

function saveDatasetChanges() {
    const datasetName = document.getElementById('DatasetNameInput').value;
    const description = document.getElementById('DescriptionTextarea').value;
    const datasetID = document.getElementById('datasetID').value;

    fetch('/api/dataset/update', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            datasetName: datasetName,
            description: description,
            datasetID : datasetID
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            //alert('Dataset information updated successfully!');
            Swal.fire({
                position: "top-middle",
                icon: "success",
                title: 'Dataset information updated successfully!',
                showConfirmButton: false,
                timer: 1500
              });
        } else {
            //alert('Error updating dataset information: ' + data.message);
            Swal.fire({
                position: "top-middle",
                icon: "error",
                title: 'Error updating dataset information!',
                showConfirmButton: true,
                confirmButtonColor: '#00243a'
            });
        }
    })
    .catch(error => {
        console.error('Error:', error);
        //alert('An error occurred while updating dataset information.');
        Swal.fire({
            position: "top-middle",
            icon: "error",
            title: 'Error updating dataset information!',
            showConfirmButton: true,
            confirmButtonColor: '#00243a'
        });
    });
}


function addDataSource() {
    const DataSourceUUID = document.getElementById('CollectedBySelect').value;
    const datasetID = document.getElementById('datasetID').value;

    fetch('/api/dataset/add_datasource', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            DataSourceUUID: DataSourceUUID,
            datasetID: datasetID
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            //alert('Dataset information updated successfully!');
            Swal.fire({
                position: "top-middle",
                icon: "success",
                title: 'Datasource added successfuly successfully!',
                showConfirmButton: false,
                timer: 1500
              });
              location.reload(true);
        } else {
            //alert('Error updating dataset information: ' + data.message);
            Swal.fire({
                position: "top-middle",
                icon: "error",
                title: 'Error adding Data Source!',
                showConfirmButton: true,
                confirmButtonColor: '#00243a'
            });
        }
    })
    .catch(error => {
        console.error('Error:', error);
        //alert('An error occurred while updating dataset information.');
        Swal.fire({
            position: "top-middle",
            icon: "error",
            title: 'Error adding Data Source!',
            showConfirmButton: true,
            confirmButtonColor: '#00243a'
        });
    });
}



function deleteDataSource(datasetUUID, datasourceUUID) {
    fetch('/api/dataset/remove_datasource', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            datasetID: datasetUUID,
            datasourceID: datasourceUUID
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            Swal.fire({
                position: "top-middle",
                icon: "success",
                title: 'Data Source removed successfully!',
                showConfirmButton: false,
                timer: 1500
            });
            location.reload(true);
        } else {
            Swal.fire({
                position: "top-middle",
                icon: "error",
                title: 'Error removing Data Source!',
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
            title: 'Error removing Data Source!',
            showConfirmButton: true,
            confirmButtonColor: '#00243a'
        });
    });
}

function deleteFile(dataset_id, file_name) {
    fetch('/api/dataset/delete_file', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            datasetID: dataset_id,
            fileName: file_name
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            Swal.fire({
                position: "top-middle",
                icon: "success",
                title: 'File deleted successfully!',
                showConfirmButton: false,
                timer: 1500
            });
        } else {
            Swal.fire({
                position: "top-middle",
                icon: "error",
                title: 'Error deleting file!',
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
            title: 'Error deleting file!',
            showConfirmButton: true,
            confirmButtonColor: '#00243a'
        });
    });
}
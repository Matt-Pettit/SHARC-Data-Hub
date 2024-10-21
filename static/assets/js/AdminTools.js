document.addEventListener('DOMContentLoaded', function() {
    const filterInput = document.getElementById("userfilter");
    const userSelect = document.getElementById("userselect");
    const roleSelect = document.getElementById("roleselect");
    const saveButton = document.getElementById("savechangesBtn");
    const changePasswdbtn = document.getElementById("changePasswd");
    const AddUserBtn = document.getElementById("adduserbtn");
    const DelUserBtn = document.getElementById("userdelbtn");
    const backupButton = document.getElementById('backupButton');
    const restoreButton = document.getElementById('restoreButton');
    const restoreFile = document.getElementById('restoreFile');
    const readOnlyToggle = document.getElementById('readOnlyToggle');

    // Function to fetch user role
    function fetchUserRole(username) {
        fetch('/api/admin/getuserrole', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username: username }),
        })
        .then(response => response.json())
        .then(data => {
            console.log(data.role);
            if (data.success) {
                roleSelect.value = data.role;
            } else {
                console.error('Failed to fetch user role:', data.message);
            }
        })
        .catch((error) => {
            console.error('Error:', error);
        });
    }

    // Event listener for user selection
    userSelect.addEventListener('change', function() {
        const selectedUsername = this.options[this.selectedIndex].value;
        console.log(selectedUsername);
        fetchUserRole(selectedUsername);
    });

    // Function to change user role
    function changeUserRole() {
        const username = userSelect.options[userSelect.selectedIndex].value;
        const role = roleSelect.value;

        fetch('/api/admin/changerole', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username: username, role: role }),
        })
        .then(response => response.json())
        .then(data => {
            console.log(data);
            if (data.success) {
                //alert('Role changed successfully: ' + data.message);
                Swal.fire({
                    position: "top-middle",
                    icon: "success",
                    title: 'Role changed successfully',
                    showConfirmButton: false,
                    timer : 1500
                });
            } else {
                //alert('Failed to change role: ' + data.message);
                //        
                Swal.fire({
                    position: "top-middle",
                    icon: "error",
                    title: 'Failed to change role!',
                    text: data.message,
                    showConfirmButton: true,
                    confirmButtonColor: '#00243a'
                });
            }
        })
        .catch((error) => {
            console.error('Error:', error);
            //alert('An error occurred while changing the role.');
            Swal.fire({
                position: "top-middle",
                icon: "error",
                title: 'Failed to change role!',
                text: error,
                showConfirmButton: true,
                confirmButtonColor: '#00243a'
            });
        });
    }


    // Function to change user  password
    function AddUser() {
        const username = document.getElementById("username").value;
        const password = document.getElementById("password").value;



        fetch('/api/admin/adduser', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 
                username: username,
                password: password,
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                Swal.fire({ 
                    position: "top-middle",
                    icon: "success",
                    title: "User added successfully!",
                    showConfirmButton: false,
                    timer: 1500
                });
                //changePasswordForm.reset();
            } else {
                Swal.fire({
                    position: "top-middle",
                    icon: "error",
                    title: "User could not be added.",
                    text: data.message,
                    confirmButtonColor: '#00243a',
                    showConfirmButton: true
                });
            }
        })
        .catch(error => {
            console.error('Error:', error);
            Swal.fire({
                position: "top-middle",
                icon: "error",
                title: "User could not be added.",
                text: error,
                confirmButtonColor: '#00243a',
                showConfirmButton: true
            } );
        });
    }

    function changeUserPassword() {
        const userSelect2 = document.getElementById("userselect2")
        const useruuid = userSelect2.options[userSelect2.selectedIndex].value;
        const newpassword = document.getElementById("newpassword").value;



        fetch('/api/usersettings/change-password', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 
                currentPassword: 'AdminReset',
                newPassword: newpassword,
                useruuid : useruuid
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                Swal.fire({ 
                    position: "top-middle",
                    icon: "success",
                    title: "Password changed successfully!",
                    showConfirmButton: false,
                    timer: 1500
                });
                //changePasswordForm.reset();
            } else {
                Swal.fire({
                    position: "top-middle",
                    icon: "error",
                    title: "Password could not be changed.",
                    text: data.message,
                    confirmButtonColor: '#00243a',
                    showConfirmButton: true
                });
            }
        })
        .catch(error => {
            console.error('Error:', error);
            Swal.fire('Error', 'An error occurred while changing the password', 'error');
        });
    }

    function DelUser() {
        const userselect3 = document.getElementById("userselect3")
        const username = userselect3.options[userselect3.selectedIndex].value;



        fetch('/api/admin/deluser', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 
                username: username,
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                Swal.fire({ 
                    position: "top-middle",
                    icon: "success",
                    title: "User deleted successfully!",
                    showConfirmButton: false,
                    timer: 1500
                });
                //changePasswordForm.reset();
            } else {
                Swal.fire({
                    position: "top-middle",
                    icon: "error",
                    title: "User could not be deleted.",
                    text: data.message,
                    confirmButtonColor: '#00243a',
                    showConfirmButton: true
                });
            }
        })
        .catch(error => {
            console.error('Error:', error);
            Swal.fire({
                position: "top-middle",
                icon: "error",
                title: "User could not be deleted.",
                text: error,
                confirmButtonColor: '#00243a',
                showConfirmButton: true
            } );
        });
    }


    // Event listener for save button
    saveButton.addEventListener('click', changeUserRole);
    changePasswdbtn.addEventListener('click', changeUserPassword);
    AddUserBtn.addEventListener('click', AddUser);
    DelUserBtn.addEventListener('click', DelUser);

    // Function to filter usernames in dropdown
    function filterUsernames() {
        const filterValue = filterInput.value.toLowerCase();
        const options = userSelect.options;

        for (let i = 0; i < options.length; i++) {
            const username = options[i].text.toLowerCase();
            if (username.includes(filterValue)) {
                options[i].style.display = '';
            } else {
                options[i].style.display = 'none';
            }
        }
    }

    // // Event listener for filter input
    // filterInput.addEventListener('input', filterUsernames);
    // if (userSelect.options.length > 0) {
    //     fetchUserRole(userSelect.options[userSelect.selectedIndex].value);
    // }

    backupButton.addEventListener('click', function() {
        console.log("Here");
        fetch('/api/admin/backup')
            .then(response => response.blob())
            .then(blob => {
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.style.display = 'none';
                a.href = url;
                a.download = 'system_backup.zip';
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
            })
            .catch(error => {
                console.error('Error downloading backup:', error);
                Swal.fire({
                    icon: 'error',
                    title: 'Backup Failed',
                    text: 'An error occurred while creating the backup.',
                });
            });
    });

    restoreButton.addEventListener('click', function() {
        console.log("Here");
        if (!restoreFile.files[0]) {
            Swal.fire({
                icon: 'warning',
                title: 'No File Selected',
                text: 'Please select a backup file to restore.',
            });
            return;
        }

        const formData = new FormData();
        formData.append('file', restoreFile.files[0]);

        fetch('/api/admin/restore', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                Swal.fire({
                    icon: 'success',
                    title: 'Restore Successful',
                    text: data.message,
                });
            } else {
                Swal.fire({
                    icon: 'error',
                    title: 'Restore Failed',
                    text: data.message,
                });
            }
        })
        .catch(error => {
            console.error('Error restoring system:', error);
            Swal.fire({
                icon: 'error',
                title: 'Restore Failed',
                text: 'An error occurred while restoring the system.',
            });
        });
    });

    readOnlyToggle.addEventListener('change', function() {
        const readOnly = this.checked;
        fetch('/api/admin/toggle_readonly', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ readOnly: readOnly })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                Swal.fire({
                    icon: 'success',
                    title: 'Mode Changed',
                    text: data.message,
                });
            } else {
                Swal.fire({
                    icon: 'error',
                    title: 'Mode Change Failed',
                    text: data.message,
                });
                this.checked = !readOnly; // Revert the toggle if the operation failed
            }
        })
        .catch(error => {
            console.error('Error toggling read-only mode:', error);
            Swal.fire({
                icon: 'error',
                title: 'Mode Change Failed',
                text: 'An error occurred while changing the system mode.',
            });
            this.checked = !readOnly; // Revert the toggle if an error occurred
        });
    });
});

function toggleDatasetApproval(datasetUUID) {
    fetch('/api/admin/toggle_dataset_approval', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ dataset_id: datasetUUID })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            Swal.fire({
                position: "top-middle",
                icon: "success",
                title: 'Dataset Approval Toggled Successfully',
                showConfirmButton: false,
                timer: 1500
            });
            window.location.reload();
        } else {
            console.error('Failed to toggle dataset approval:', data.message);
            Swal.fire({
                position: "top-middle",
                icon: "error",
                title: 'Failed to toggle dataset approval!',
                text: data.message,
                showConfirmButton: true,
                confirmButtonColor: '#00243a'
            });
        }
    })
    .catch(error => {
        console.error('Error toggling dataset approval:', error);
        Swal.fire({
            position: "top-middle",
            icon: "error",
            title: 'Failed to toggle dataset approval!',
            text: error,
            showConfirmButton: true,
            confirmButtonColor: '#00243a'
        });
    });
}

// Handler to upload a encoder or decoder file as specified by the type
function uploadEncoderDecoder(type) {
    const fileInput = document.getElementById(`${type}Upload`);
    const files = fileInput.files;
    // Collect All Files 
    if (files.length === 0) {
        Swal.fire({
            position: "top-middle",
            icon: "warning",
            title: `Please select one or more ${type} files to upload.`,
            showConfirmButton: false,
            timer: 1500
        });
        return;
    }
    const formData = new FormData();
    for (let i = 0; i < files.length; i++) {
        formData.append('files', files[i]);
    }
    formData.append('type', type);
    // Perform POST request with files
    fetch('/api/admin/upload_encoder_decoder', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Successful Operation
            Swal.fire({
                position: "top-middle",
                icon: "success",
                title: `Successfully uploaded ${type} file(s)!`,
                showConfirmButton: false,
                timer: 1500
            });
            fileInput.value = ''; 
        } else {
            // Unsuccessful Operation
            Swal.fire({
                position: "top-middle",
                icon: "error",
                title: `Error uploading ${type} files!`,
                text: data.message,
                showConfirmButton: true,
                confirmButtonColor: '#00243a'
            });
        }
    })
    // Catch general errors
    .catch(error => {
        console.error('Error:', error);
        Swal.fire({
            position: "top-middle",
            icon: "error",
            title: `Error uploading ${type} files!`,
            text: 'An unexpected error occurred.',
            showConfirmButton: true,
            confirmButtonColor: '#00243a'
        });
    });
}


// File Deleter Function with Confirmation
function confirmDelete(title, text, apiUrl, successMessage, errorMessage, data) {
    Swal.fire({
        title: title,
        text: text,
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#00243a',
        cancelButtonColor: '#d33',
        confirmButtonText: 'Yes, delete it!'
    }).then((result) => {
        if (result.isConfirmed) {
            fetch(apiUrl, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(data)
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    Swal.fire({
                        position: "top-middle",
                        icon: "success",
                        title: successMessage,
                        showConfirmButton: false,
                        timer: 1500
                    });
                    location.reload(true);
                } else {
                    Swal.fire({
                        position: "top-middle",
                        icon: "error",
                        title: errorMessage,
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
                    title: errorMessage,
                    text: 'An error occurred while performing the operation.',
                    showConfirmButton: true,
                    confirmButtonColor: '#00243a'
                });
            });
        }
    });
}

function confirmDeleteFile(type, name) {
    confirmDelete(
        'Are you sure?',
        'Do you want to remove the file?',
        '/api/admin/delete_file',
        'File removed successfully!',
        'Error removing File!',
        { type: type, filename: name }
    );
}


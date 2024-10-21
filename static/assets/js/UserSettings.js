document.addEventListener('DOMContentLoaded', function() {
    const changePasswordForm = document.getElementById('changePasswordForm');
    
    changePasswordForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const currentPassword = document.getElementById('currentPassword').value;
        const newPassword = document.getElementById('newPassword').value;
        const confirmPassword = document.getElementById('confirmPassword').value;
        const useruuid = document.getElementById('useruuid').value;
        
        if (newPassword !== confirmPassword) {
            Swal.fire({
                position: "top-middle",
                icon: "warning",
                title: "Password do not match",
                text: "Please ensure that both passwords are the same.",
                showConfirmButton: false,
                timer : 1500
            });
            return;
        }
        
        fetch('/api/usersettings/change-password', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 
                currentPassword: currentPassword,
                newPassword: newPassword,
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
    });
});


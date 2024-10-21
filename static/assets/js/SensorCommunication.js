// Function to upload files to the "Communication From Data Source" API endpoint
function uploadFromDataSource() {
    // Get references to the DOM elements
    const fileInput = document.getElementById("IridiumCSVPicker");
    const optionsFileInput = document.getElementById("OptsFilePicker");
    const decoderSelect = document.getElementById("DecoderSelector");
    // const processButton = document.getElementById(processButtonId);
  
    // Get the selected files and options file (if provided)
    const files = fileInput.files;
    const optionsFile = optionsFileInput.files.length > 0 ? optionsFileInput.files[0] : null;
    const decoder = decoderSelect.value;
  
    // Validate input
    if (files.length === 0) {
      //alert('Please select a file to upload.');
      Swal.fire({
        position: "top-middle",
        icon: "warning",
        title: "Please select a file to upload.",
        showConfirmButton: false,
        timer: 1500
      });
      return;
    }
  
    // Create a FormData object to hold the files and options file
    const formData = new FormData();
    formData.append('file', files[0]);
    if (optionsFile) {
      formData.append('options_file', optionsFile);
    }
    formData.append('decoder', decoder);
  
    // Send the files to the "Communication From Data Source" API endpoint
    fetch('/api/datasourcecommunication/upload-from', {
      method: 'POST',
      body: formData
    })
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        //alert('Files uploaded and processed successfully!');
        Swal.fire({
          position: "top-middle",
          icon: "success",
          title: 'File(s) uploaded and processed successfully!',
          showConfirmButton: false,
          timer: 1500
      });
        // Clear the file inputs
        fileInput.value = '';
        optionsFileInput.value = '';
        document.getElementById("FromOutput").innerText = data.output;
      } else {
        alert(`Error: ${data.message}`);
        Swal.fire({
          position: "top-middle",
          icon: "error",
          title: 'Error uploading file(s)!',
          text: data.message,
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
        title: 'Error uploading file(s)!',
        text: data.message,
        showConfirmButton: true,
        confirmButtonColor: '#00243a'
      });
    });
  }
  
// Function to upload files to the "Communication To Data Source" API endpoint
function uploadToDataSource() {
    // Get references to the DOM elements
    const fileInput = document.getElementById("FileSendPicker");
    const optionsFileInput = document.getElementById("SendOptsFilePicker");
    const encoderSelect = document.getElementById("EncoderSelector");

    // Get the selected files and options file (if provided)
    const files = fileInput.files;
    const optionsFile = optionsFileInput.files.length > 0 ? optionsFileInput.files[0] : null;
    const encoder = encoderSelect.value;

    // Validate input
    if (files.length === 0) {
        //alert('Please select a file to upload.');
        Swal.fire({
          position: "top-middle",
          icon: "warning",
          title: "Please select a file to upload.",
          showConfirmButton: false,
          timer: 1500
        });
        return;
    }

    // Create a FormData object to hold the files and options file
    const formData = new FormData();
    formData.append('file', files[0]);
    if (optionsFile) {
        formData.append('options_file', optionsFile);
    }
    formData.append('encoder', encoder);

    // Send the files to the "Communication To Data Source" API endpoint
    fetch('/api/datasourcecommunication/upload-to', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
       // alert('Files uploaded and processed successfully!');
        Swal.fire({
            position: "top-middle",
            icon: "success",
            title: 'File(s) uploaded and processed successfully!',
            showConfirmButton: false,
            timer: 1500
        });
        // Clear the file inputs
        fileInput.value = '';
        optionsFileInput.value = '';
        document.getElementById("ToOutput").innerText = data.output;

        } else {
        //alert(`Error: ${data.message}`);
        Swal.fire({
          position: "top-middle",
          icon: "error",
          title: 'Error uploading file(s)!',
          text: data.message,
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
          title: 'Error uploading file(s)!',
          text: data.message,
          showConfirmButton: true,
          confirmButtonColor: '#00243a'
        });
    });
}


// Communication From Data Source
document.getElementById('DecodeProcessBtn').addEventListener('click', () => {
    uploadFromDataSource();
});
  
// Communication To Data Source
document.getElementById('EncodeProcessBtn').addEventListener('click', () => {
    uploadToDataSource();
});
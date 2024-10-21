function submitAllForms() {
          // Create a new FormData object
          let formData = new FormData();
          
          // Collect data from form1
          let form1 = document.getElementById('formSearch');
          for (let i = 0; i < form1.elements.length; i++) {
            formData.append(form1.elements[i].name, form1.elements[i].value);
          }
          
          // Collect data from form2
          let form2 = document.getElementById('formOptions');
          for (let i = 0; i < form2.elements.length; i++) {
            formData.append(form2.elements[i].name, form2.elements[i].value);
          }
          
          // Send the data using fetch
          fetch('/datasearch', {
            method: 'POST',
    body: formData
  })
  .then(response => response.text())
  .then(html => {
    // Replace the entire document with the received HTML
    document.open();
    document.write(html);
    document.close();
  })
  .catch(error => console.error('Error:', error));
}


function submitTopSearchForm(event) {
    event.preventDefault(); // Prevent the default form submission

    // Get the small top search bar input
    const topSearchInput = document.querySelector('.navbar-search input');
    
    // Create a new FormData object and append the search input value
    const formData = new FormData();
    formData.append('TextSearch', topSearchInput.value);

    // Send the data using fetch
    fetch('/datasearch', {
        method: 'POST',
        body: formData
    })
    .then(response => response.text())
    .then(html => {
        // Replace the entire document with the received HTML
        document.open();
        document.write(html);
        document.close();
    })
    .catch(error => console.error('Error:', error));
}

// Add event listener to the top search button
document.addEventListener('DOMContentLoaded', function() {
    const topSearchButton = document.querySelector('.navbar-search button');
    topSearchButton.addEventListener('click', submitTopSearchForm);
});
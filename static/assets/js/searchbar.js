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
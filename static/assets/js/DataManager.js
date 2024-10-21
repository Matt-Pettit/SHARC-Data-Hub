document.addEventListener('DOMContentLoaded', function() {
    const createButton = document.getElementById('CreateNewdataset');
    const datasourceSelect = document.getElementById('DatasourceSelect');

    createButton.addEventListener('click', function() {
        const selectedDatasource = datasourceSelect.value;
        if (selectedDatasource) {
            window.location.href = `/datasetcreator/${selectedDatasource}`;
        } else {
            alert('Please select a Data Source before creating a new Data Set.');
        }
    });
});

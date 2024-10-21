const antarctic = new L.Proj.CRS('EPSG:3031',
    '+proj=stere +lat_0=-90 +lat_ts=-71 +lon_0=0 +k=1 +x_0=0 +y_0=0 +datum=WGS84 +units=m +no_defs',
    {
        origin: [-4194304, 4194304],
        resolutions: [
        8192.0,
        4096.0,
        2048.0,
        1024.0,
        512.0,
        256.0,
        128.0,
        64.0,
        32.0
        ]
    }
);
// Initialize the map
const map = L.map('map', {
    center: [-90, 0],
    zoom: 0.25,
    crs: antarctic,
    maxZoom: 100
});

// Add a plain light gray background
L.tileLayer('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+ip1sAAAAASUVORK5CYII=', {
    attribution: 'Base map'
}).addTo(map);

// Add a GeoJSON layer for Antarctic borders
fetch('/static/assets/countriesmini.geojson')
    .then(response => response.json())
    .then(data => {
        L.geoJSON(data, {
        style: {
            color: '#00243a',
            weight: 2,
            opacity: 0.65
        }
        }).addTo(map);
    });

// Updating Coordinate Dispalay
L.Control.Coordinates = L.Control.extend({
    onAdd: function(map) {
        const container = L.DomUtil.create('div', 'leaflet-control-coordinates');
        container.style.background = 'rgba(255, 255, 255, 0.7)';
        container.style.padding = '5px';
        container.style.margin = '10px';
        container.style.border = '1px solid #ccc';
        container.style.borderRadius = '5px';
        this._container = container;
        return container;
    },

    updateHTML: function(lat, lng) {
        this._container.innerHTML = `Lat: ${lat.toFixed(6)}, Long: ${lng.toFixed(6)}`;
    }
});
L.control.coordinates = function(opts) {
    return new L.Control.Coordinates(opts);
}
const coordinatesControl = L.control.coordinates({ position: 'bottomleft' }).addTo(map);
// Update coordinates when mouse moves
map.on('mousemove', function(e) {
    const { lat, lng } = e.latlng;
    coordinatesControl.updateHTML(lat, lng);
});


// Function to toggle all checkboxes in the table
function toggleAllCheckboxes(tableId) {
    const checkboxes = document.querySelectorAll(`#${tableId} input[type="checkbox"]`);
    const allChecked = Array.from(checkboxes).every(cb => cb.checked);
    checkboxes.forEach(cb => cb.checked = !allChecked);
}

// Function to populate dropdowns and table with column names
function populateColumnOptions(columns) {
    document.getElementById('columnsTableMain').style.display='block'; 

    const latSelect = document.getElementById('latitudeSelect');
    const lonSelect = document.getElementById('longitudeSelect');
    const columnsTable = document.getElementById('columnsTable').getElementsByTagName('tbody')[0];

    latSelect.innerHTML = '';
    lonSelect.innerHTML = '';
    columnsTable.innerHTML = '';

    columns.forEach(column => {
        // Add to latitude and longitude dropdowns
        latSelect.add(new Option(column, column));
        lonSelect.add(new Option(column, column));

        // Add to columns table
        const row = columnsTable.insertRow();
        const cell1 = row.insertCell(0);
        const cell2 = row.insertCell(1);
        cell2.style= "text-align: center;"
        cell1.textContent = column;
        cell2.innerHTML = '<input type="checkbox">';
    });
}

// Event listener for file selection
document.getElementById('fileSelect').addEventListener('change', function() {
    const selectedFile = this.value;
    const datasetID = document.getElementById('datasetID').value;
    // Make API request to get column names
    fetch('/api/dataset/getcolumns', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            file: selectedFile,
            dataset_id: datasetID
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            populateColumnOptions(data.columns);
        } else {
            console.error('Error:', data.message);
            alert('Error fetching column names: ' + data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error fetching column names');
    });
});

// Event listener for toggle button
document.getElementById('toggleFilesBtn').addEventListener('click', () => toggleAllCheckboxes('filesTable'));

// Event listener for create map button
document.getElementById('createMapBtn').addEventListener('click', function() {
    const selectedColumns = Array.from(document.querySelectorAll('#columnsTable input[type="checkbox"]:checked'))
        .map(cb => cb.closest('tr').cells[0].textContent);
    document.getElementById('map').style.display = 'block';
    document.getElementById('columnsTableMain').style.display = 'none';
    document.getElementById('clearMap').style.display = 'block';
    const latColumn = document.getElementById('latitudeSelect').value;
    const lonColumn = document.getElementById('longitudeSelect').value;
    const selectedFile = document.getElementById('fileSelect').value;
    // Make API request to get map data
    fetch('/api/dataset/getmapdata', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            file: selectedFile,
            dataset_id: document.getElementById('datasetID').value,
            lat_column: latColumn,
            lon_column: lonColumn,
            data_columns: selectedColumns
        }),
    })
    .then(response => response.json())
    .then(data => {
        console.log(data);
        updateMap(data);
    })
    .catch(error => console.error('Error:', error));
});


// Function to find color value between two colors
const interpolateColor = (color1, color2, factor) => {
    const result = color1.slice();
    for (let i = 0; i < 3; i++) {
        result[i] = Math.round(result[i] + factor * (color2[i] - color1[i]));
    }
    return result;
};

// Function to update the map with new data
function updateMap(data) {
    // Clear existing layers
    map.eachLayer(layer => {
        if (layer instanceof L.CircleMarker) {
            map.removeLayer(layer);
        }
    });

    // If there's only one data column selected
    if (data.data[0].Row.length === 1) {
        const [columnName, ] = data.data[0].Row[0];
        const values = data.data.map(item => parseFloat(item.Row[0][1]));
        const minValue = Math.min(...values);
        const maxValue = Math.max(...values);

        // Get color based on value
        const getColor = (value) => {
            const factor = (value - minValue) / (maxValue - minValue);
            const lowColor = [0, 0, 255];  // Blue
            const highColor = [255, 0, 0]; // Red
            const interpolated = interpolateColor(lowColor, highColor, factor);
            return `rgb(${interpolated[0]}, ${interpolated[1]}, ${interpolated[2]})`;
        };

        data.data.forEach(item => {
            const [lat, lon] = item.Location.split(',').map(Number);
            const value = parseFloat(item.Row[0][1]);
            const color = getColor(value);

            const marker = L.circleMarker([lat, lon], {
                radius: 5,
                color: color,
                fillColor: color,
                fillOpacity: 0.7
            }).addTo(map);

            let popupContent = `<h3>Location: ${lat}, ${lon}</h3>`;
            popupContent += `<p>${columnName}: ${value}</p>`;
            marker.bindPopup(popupContent);
        });
    } else {
        // If multiple columns are selected, use makes all values the same color
        data.data.forEach(item => {
            try {
                const [lat, lon] = item.Location.split(',').map(Number);
                const marker = L.circleMarker([lat, lon], {
                    radius: 5,
                    color: "#fc1303",
                    fillColor: "#fc1303",
                    fillOpacity: 0.7
                }).addTo(map);

                let popupContent = `<h3>Location: ${lat}, ${lon}</h3>`;
                item.Row.forEach(([columnName, value]) => {
                    popupContent += `<p>${columnName}: ${value}</p>`;
                });
                marker.bindPopup(popupContent);
            }   catch (err) {
                console.log(err)
            }
        });
    }
}

// Function to handle file downloads
function downloadSelectedFiles() {
    const selectedFiles = Array.from(document.querySelectorAll('#filesTable input[type="checkbox"]:checked'))
        .map(cb => ({
            filename: cb.closest('tr').cells[0].textContent,
        }));

    const datasetId = document.getElementById('datasetID').value;

    if (selectedFiles.length === 0) {
        alert('Please select at least one file to download.');
        return;
    }

    selectedFiles.forEach(file => {
        downloadFile(datasetId, file.filename);
    });
}

// Function to download a single file
function downloadFile(datasetId, filename) {
    fetch('/api/dataset/downloadfile', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            dataset_id: datasetId,
            filename: filename
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.blob();
    })
    .then(blob => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
    })
    .catch(error => {
        console.error('Error downloading file:', error);
        alert(`Error downloading ${filename}. Please try again.`);
    });
}

document.getElementById('clearMap').addEventListener('click', function() {

    document.getElementById('columnsTableMain').style.display='block'; //to show
    document.getElementById('clearMap').style.display='none'; //to hide
});


// Add event listener to the download button
document.addEventListener('DOMContentLoaded', () => {
    const downloadButton = document.getElementById('downloadButton');
    if (downloadButton) {
        downloadButton.addEventListener('click', downloadSelectedFiles);
    }
    document.getElementById('map').style.display='none'; //to hide
    document.getElementById('columnsTableMain').style.display='none'; //to hide
});
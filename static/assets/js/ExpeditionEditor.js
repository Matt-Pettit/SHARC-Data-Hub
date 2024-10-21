// Function to save expedition changes
function saveExpeditionChanges() {
    const expeditionUUID = document.getElementById('ExpeditionUUID').value;
    const expeditionName = document.getElementById('ExpName').value;
    const expeditionDescription = document.getElementById('ExpDesc').value;
    const startDate = document.getElementById('startdate').value;
    const endDate = document.getElementById('enddate').value;

    fetch('/api/expedition/update', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            expeditionUUID: expeditionUUID,
            name: expeditionName,
            description: expeditionDescription,
            startDate: startDate,
            endDate: endDate
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            Swal.fire({
                position: "top-middle",
                icon: "success",
                title: "Expedition updated successfully!",
                showConfirmButton: false,
                timer: 1500
            });
        } else {
            Swal.fire({
                position: "top-middle",
                icon: "error",
                title: "Failed to update expedition",
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
            title: "An error occurred",
            text: "Failed to update expedition",
            confirmButtonColor: '#00243a',
            showConfirmButton: true
        });
    });
}



// Function to add a researcher
function addResearcher() {
    const expeditionUUID = document.getElementById('ExpeditionUUID').value;
    const researcherUUID = document.getElementById('ResearcherSelect').value;

    fetch('/api/expedition/add_researcher', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            expeditionUUID: expeditionUUID,
            researcherUUID: researcherUUID
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            Swal.fire({
                position: "top-middle",
                icon: "success",
                title: "Researcher added successfully!",
                showConfirmButton: false,
                timer: 1500
            }).then(() => {
                location.reload(true);
            });
        } else {
            Swal.fire({
                position: "top-middle",
                icon: "error",
                title: "Failed to add researcher",
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
            title: "An error occurred",
            text: "Failed to add researcher",
            confirmButtonColor: '#00243a',
            showConfirmButton: true
        });
    });
}

// Function to add a datasource
function addDatasource() {
    const expeditionUUID = document.getElementById('ExpeditionUUID').value;
    const datasourceUUID = document.getElementById('DatasourceSelect').value;
    console.log(expeditionUUID);
    console.log(datasourceUUID);
    fetch('/api/expedition/add_datasource', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            expeditionUUID: expeditionUUID,
            datasourceUUID: datasourceUUID
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            Swal.fire({
                position: "top-middle",
                icon: "success",
                title: "Datasource added successfully!",
                showConfirmButton: false,
                timer: 1500
            }).then(() => {
                location.reload(true);
            });
        } else {
            Swal.fire({
                position: "top-middle",
                icon: "error",
                title: "Failed to add datasource",
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
            title: "An error occurred",
            text: "Failed to add datasource",
            confirmButtonColor: '#00243a',
            showConfirmButton: true
        });
    });
}


function DeleteExpedition() {
    const expeditionUUID = document.getElementById('ExpeditionUUID').value;
    console.log(expeditionUUID);
    fetch('/api/expedition/delete', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            expeditionUUID: expeditionUUID,
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            Swal.fire({
                position: "top-middle",
                icon: "success",
                title: "Expedition deleted successfully!",
                showConfirmButton: false,
                timer: 1500
            }).then(() => {
                location.reload(true);
            });
        } else {
            Swal.fire({
                position: "top-middle",
                icon: "error",
                title: "Failed to delete Expedition!",
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
            title: "An error occurred",
            text: "Failed to delete Expedition!",
            confirmButtonColor: '#00243a',
            showConfirmButton: true
        });
    });
}

// Function to handle expedition selection change
function handleExpeditionChange() {
    const selectedExpeditionUUID = document.getElementById('ExpeditionSelect').value;
    const currentExpeditionUUID = document.getElementById('ExpeditionUUID').value;

    if (selectedExpeditionUUID !== currentExpeditionUUID) {
        window.location.href = `/expeditioneditor/${selectedExpeditionUUID}`;
    }
}
const expeditionSelect = document.getElementById('ExpeditionSelect');
// Event listeners
document.addEventListener('DOMContentLoaded', function() {
    expeditionSelect.addEventListener('change', handleExpeditionChange);
    document.getElementById('SaveChangesBtn').addEventListener('click', saveExpeditionChanges);
    document.getElementById('AddResearcherBtn').addEventListener('click', addResearcher);
    document.getElementById('AddDatasourceBtn').addEventListener('click', addDatasource);
    document.getElementById('CreateNewExpBtn').addEventListener('click', function() {
        window.location.href = '/expeditioneditor/new';
    });

});

// Initialize the map with Antarctic projection
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
    256.0
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

// Show coordinates control only when drawing
map.on(L.Draw.Event.DRAWSTART, function() {
    coordinatesControl.addTo(map);
});

map.on(L.Draw.Event.DRAWSTOP, function() {
    map.removeControl(coordinatesControl);
});
// Layer for storing drawn items
const drawnItems = new L.FeatureGroup();
map.addLayer(drawnItems);

// Add Leaflet.draw controls with custom labels
const drawControl = new L.Control.Draw({
    draw: {
        polyline: {
            shapeOptions: {
                color: '#3388ff',
                weight: 3
            }
        },
        polygon: {
            shapeOptions: {
                color: '#ff6666',
                weight: 3
            }
        },
        marker: true,
        circle: false,
        rectangle: false,
        circlemarker: false
    },
    edit: {
        featureGroup: drawnItems
    }
});

map.addControl(drawControl);

// Customize draw control labels
L.drawLocal.draw.toolbar.buttons.polyline = 'Draw route';
L.drawLocal.draw.toolbar.buttons.polygon = 'Draw area';
L.drawLocal.draw.toolbar.buttons.marker = 'Place objective';

// Function to save drawn items to the server
function saveDrawnItemsToDatabase(items, expeditionUuid) {
    fetch('/api/expedition/save_drawn_items', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        expeditionUuid: expeditionUuid,
        items: items
      })
    })
      .then(response => {
        if (!response.ok) {
          throw new Error('Failed to save items');
        }
        return response.json();
      })
      .then(data => {
        console.log('Items saved successfully:');
      })
      .catch(error => {
        console.error('Error saving items:', error);
      });
  }

map.on(L.Draw.Event.CREATED, function (event) {
    const layer = event.layer;
    const type = event.layerType;

    // Function to show SweetAlert2 prompt
    const showPrompt = (title, inputPlaceholder) => {
        return Swal.fire({
            title: title,
            input: 'text',
            inputPlaceholder: inputPlaceholder,
            showCancelButton: true,
            confirmButtonColor: '#00243a',
            cancelButtonColor: '#d33',
            confirmButtonText: 'Save',
            cancelButtonText: 'Cancel'
        });
    };

    let promptConfig;
    switch (type) {
        case 'polyline':
            promptConfig = {
                title: 'Enter route description:',
                placeholder: 'Route description'
            };
            break;
        case 'polygon':
            promptConfig = {
                title: 'Enter area description:',
                placeholder: 'Area description'
            };
            break;
        case 'marker':
            const { lat, lng } = layer.getLatLng();
            promptConfig = {
                title: `Enter objective description:`,
                placeholder: `Objective at Lat: ${lat.toFixed(6)}, Long: ${lng.toFixed(6)}`
            };
            break;
        case 'point':
                const { lat2, lng2 } = layer.getLatLng();
                promptConfig = {
                    title: `Enter objective description:`,
                    placeholder: `Objective at Lat: ${lat2.toFixed(6)}, Long: ${lng2.toFixed(6)}`
            };
            break;
        
    }

    showPrompt(promptConfig.title, promptConfig.placeholder).then((result) => {
        if (result.isConfirmed) {
            const popupdesc = result.value || 'No description provided';

            let popupContent = '<table>';
            popupContent += `<tr><td>Description</td><td>${popupdesc}</td></tr>`;
            
            popupContent += '</table>';
            layer.bindPopup(popupContent);
            drawnItems.addLayer(layer);

            saveAllDrawnItems();
        }
        // Remove coordinates control after drawing
        map.removeControl(coordinatesControl);
    });
});


// Modify the event listeners for editing and deleting
map.on(L.Draw.Event.EDITED, function(event) {
    const layers = event.layers;
    layers.eachLayer(function(layer) {
        // Update the layer properties if needed
        if (layer.getPopup()) {
            layer.setPopupContent(layer.getPopup().getContent());
        }
    });
    saveAllDrawnItems();
});

map.on(L.Draw.Event.DELETED, function(event) {
    saveAllDrawnItems(); // This will now only save the remaining items
});

function getSensorData() {
    const expeditionUUID = document.getElementById('ExpeditionUUID').value;
    fetch('/api/expedition/get_datasource_data', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            expeditionUuid: expeditionUUID
        })
    })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            //console.log('Sensor data:', data);
            const colorMap = {};

            const getColor = (name) => {
                if (!colorMap[name]) {
                    colorMap[name] = '#' + Math.floor(Math.random() * 16777215).toString(16);
                }
                return colorMap[name];
            };

            data.forEach(sensor => {
                const [lat, lon] = sensor['Location'].split(',').map(Number);
                const color = getColor(sensor['Sensor Name']);
                L.circleMarker([lat, lon], {
                    radius: 10,
                    color: color,
                    fillColor: color,
                    fillOpacity: 0.7
                })
                    .addTo(map)
                    .bindPopup(`
                        <h3>${sensor['Sensor Name']}</h3>
                        <div class="text-center">
                            <img class="rounded" src="/api/datasource/${sensor['UUID']}/image" width="120" height="auto" style="margin: 0 auto;">
                        </div>
                        <img  width="100"> 
                        <p>Time: ${sensor['Time']}</p>
                        <p>Location: ${lat}, ${lon}</p>
                    `)
                    .on('click', function() {
                        showDatasets(sensor['UUID']);
                    });
            });
        })
        .catch(error => {
            console.error('There was a problem with the fetch operation:', error.message);
        });
}



// Performance version adapted from previous.
function loadDrawnItemsFromDatabase(expeditionUuid) {
    console.log(expeditionUuid)
    fetch('/api/expedition/load_drawn_items', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            expeditionUuid: expeditionUuid
        })
    })
    .then(response => {
        if (!response.ok) {
          throw new Error('Failed to load items');
        }
        return response.json();
    })
    .then(data => {
        const batchSize = 200;
        let index = 0;
        processBatch(data,batchSize,index); 
    })
      .catch(error => {
        console.error('Error loading drawn items:', error);
    });
}

// Recursive function to process all of the data in batches.
// THis is done for performance reasons, but also happens to make a cool animation replaying the progress if the dataset is huge.       
function processBatch(data,batchSize,index) {
    const end = Math.min(index + batchSize, data.length);
    for (let i = index; i < end; i++) {
        const item = data[i];
        let layer = createLayer(item);
        if (layer) {
        drawnItems.addLayer(layer);
        bindPopup(layer, item.properties);
        }
    }
    index = end;
    if (index < data.length) {
        // schedule next batch
        //setTimeout(processBatch, 0);
        setTimeout(() => processBatch(data, batchSize, index), 0);
    }
}

function createLayer(item) {
    let layer;
    if (item.geometry.type === 'Polygon') {
        const swappedCoordinates = item.geometry.coordinates.map(ring =>
        ring.map(coord => [coord[1], coord[0]])
        );
        layer = L.polygon(swappedCoordinates);
        } 
    else if (item.geometry.type === 'Marker' || item.geometry.type === 'Point') {
        layer = L.marker([item.geometry.coordinates[1], item.geometry.coordinates[0]]);
        } 
    else if (item.geometry.type === 'LineString') {
        const swappedCoordinates = item.geometry.coordinates.map(coord =>
        [coord[1], coord[0]]
        );
        layer = L.polyline(swappedCoordinates);
    }
    return layer;
}



function bindPopup(layer, properties) {
    let popupContent = '<table>';
    for (let k in properties) {
        popupContent += `<tr><td>${k}</td><td>${properties[k]}</td></tr>`;
    }
    popupContent += '</table>';
    layer.bindPopup(popupContent);
}



function tableStringToDict(tableString) {
    // Parse into a document using DOMParser object
    const parser = new DOMParser();
    const doc = parser.parseFromString(tableString, 'text/html');
    const table = doc.querySelector('table');
    const dict = {};
    
    // Loop through the rows and extract key-value pairs
    for (let row of table.rows) {
        let key = row.cells[0].innerText.trim();
        let value = row.cells[1].innerText.trim();
        dict[key] = value;
    }
    
    return dict;
}


// Function to save all drawn items
function saveAllDrawnItems() {
    const expeditionUUID = document.getElementById('ExpeditionUUID').value;
    const allDrawnItems = [];
    drawnItems.eachLayer(layer => {
      const drawnItem = {
        type: layer instanceof L.Marker ? 'marker' :
          layer instanceof L.Polyline && !(layer instanceof L.Polygon) ? 'polyline' :
            layer instanceof L.Polygon ? 'polygon' : 'unknown',
        geometry: layer.toGeoJSON().geometry,
        properties: tableStringToDict(layer.getPopup()["_content"])
      };
      //console.log(tableStringToDict(layer.getPopup()["_content"]))
      allDrawnItems.push(drawnItem);
    });
    //console.log(allDrawnItems);
    saveDrawnItemsToDatabase(allDrawnItems, expeditionUUID);
  }


// Function to make routes editable
function makeRoutesEditable() {
    drawnItems.eachLayer(layer => {
        if (layer instanceof L.Polyline && !(layer instanceof L.Polygon)) {
            layer.editing.enable();
            layer.on('edit', saveAllDrawnItems);
        }
    });
}

function makeMarkersEditable() {
    drawnItems.eachLayer(layer => {
        if (layer instanceof L.Marker) {
            layer.dragging.enable();
            layer.on('dragend', saveAllDrawnItems);
        }
    });
}

function makeAreasEditable() {
    drawnItems.eachLayer(layer => {
        if (layer instanceof L.Polygon) {
            layer.editing.enable();
            layer.on('edit', saveAllDrawnItems);
        }
    });
}


function FileUpload() {
    const expeditionUUID = document.getElementById('ExpeditionUUID').value;
    Swal.fire({
        title: 'Upload a file',
        input: 'file',
        inputAttributes: {
            'accept': '*/*',
            'aria-label': 'Upload your file'
        },
        showCancelButton: true,
        confirmButtonText: 'Upload',
        showLoaderOnConfirm: true,
        confirmButtonColor: "#00243a",
        preConfirm: (file) => {
            if (!file) {
                Swal.showValidationMessage('Please select a file');
                return false;
            }
            const formData = new FormData();
            formData.append('file', file);
            formData.append('expeditionUUID', expeditionUUID);
            return fetch('/api/expedition/upload_file', {
                method: 'POST',
                body: formData
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error(response.statusText);
                }
                return response.json();
            })
            .catch(error => {
                Swal.showValidationMessage(`Upload failed: ${error.message}`);
            });
        },
        allowOutsideClick: () => !Swal.isLoading()
    }).then((result) => {
        if (result.isConfirmed) {
            Swal.fire({
                icon: "success",
                title: 'Successfully uploaded file!',
                showConfirmButton: false,
                timer: 1500
            });
        }
    });
}


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
                headers: {
                    'Content-Type': 'application/json'
                },
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

function confirmRemoveDataSource(expeditionUUID, dataSourceUUID) {
    confirmDelete(
        'Are you sure?',
        `Do you want to remove the data source?`,
        '/api/expedition/remove_datasource',
        'Data source removed successfully!',
        'Error removing data source!',
        { expeditionUUID, datasourceUUID: dataSourceUUID }
    );
}

function confirmRemoveUser(expeditionUUID, userUUID) {
    console.log("User:");
    console.log(userUUID);
    confirmDelete(
        'Are you sure?',
        `Do you want to remove the user?`,
        '/api/expedition/remove_user',
        'User removed successfully!',
        'Error removing user!',
        { expeditionUUID, userUUID }
    );
}




const expeditionUUID = document.getElementById('ExpeditionUUID').value;
console.log(expeditionUUID)
loadDrawnItemsFromDatabase(expeditionUUID);

// Enable editing mode for all types of drawn items
makeRoutesEditable();
makeMarkersEditable();
makeAreasEditable();
getSensorData();
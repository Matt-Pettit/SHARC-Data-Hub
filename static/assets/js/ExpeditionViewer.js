// Function to handle expedition selection change
function handleExpeditionChange() {
    const selectedExpeditionUUID = document.getElementById('ExpeditionSelect').value;
    const currentExpeditionUUID = document.getElementById('ExpeditionUUID').value;

    if (selectedExpeditionUUID !== currentExpeditionUUID) {
        window.location.href = `/expedition/${selectedExpeditionUUID}`;
    }
}

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

const expeditionUUID = document.getElementById('ExpeditionUUID').value;
loadDrawnItemsFromDatabase(expeditionUUID);

getSensorData();


const expeditionSelect = document.getElementById('ExpeditionSelect')
expeditionSelect.addEventListener('change', handleExpeditionChange);



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

map.on('click', function(e) {
    const lat = e.latlng.lat.toFixed(4);
    const lng = e.latlng.lng.toFixed(4);
    
    L.popup()
        .setLatLng(e.latlng)
        .setContent(`Latitude: ${lat}<br>Longitude: ${lng}`)
        .openOn(map);
});

// Add a plain light gray background
L.tileLayer('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+ip1sAAAAASUVORK5CYII=', {
attribution: 'Base map'
}).addTo(map);




// Define the Antarctic regions with lists of coordinates
const antarcticRegions = {

};

// Function to create a polygon for each region
function createRegionPolygon(coords) {
return coords.concat([[-90, coords[coords.length - 1][1]], [-90, coords[0][1]]]);
}

// Add GeoJSON layers for Antarctic regions
Object.entries(antarcticRegions).forEach(([name, coords]) => {
const polygon = createRegionPolygon(coords);
L.polygon(polygon, {
color: getRandomColor(),
fillOpacity: 0.3,
weight: 1
}).addTo(map).bindPopup(name);
});

// Function to generate random colors
function getRandomColor() {
return '#' + Math.floor(Math.random()*16777215).toString(16);
}

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





function getSensorData() {
    fetch('/api/datasource/getlocationdata', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({}) // You can add request parameters here if needed
    })
    .then(response => {
        console.log(response);
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        console.log(data);
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
                <img width="100">
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

function showDatasets(datasourceUUID) {
    fetch('/api/datasource/getdatasets', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ datasourceUUID: datasourceUUID })
    })
    .then(response => response.json())
    .then(datasets => {
        const container = document.getElementById('dataset-container');
        container.innerHTML = ''; // Clear previous content
        container.style.display = 'flex'; // Unhide Container

        // For all the datasets in the response populate the Dataset blocks
        datasets.forEach(dataset => {
            const datasetBlock = document.createElement('div');
            datasetBlock.className = 'dataset-block';
            datasetBlock.innerHTML = `
                <h6>${dataset['Dataset Name']}</h6>
                <div class="button-container">
                    <a href="/datadownload/${dataset['DatasetUUID']}" class="btn btn-primary" style="background: rgb(0, 36, 58);border-color: rgb(0, 36, 58);" type="button">Download</a>
                </div>`;
            container.appendChild(datasetBlock);
        });
    })
    .catch(error => {
        console.error('Error fetching datasets:', error);
    });
}

getSensorData();



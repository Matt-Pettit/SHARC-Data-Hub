self.onmessage = function(e) {
    if (e.data.action === 'processDrawnItems') {
      const processedItems = e.data.data.map(item => {
        let geometry;
        if (item.geometry.type === 'Polygon') {
          geometry = {
            type: 'Polygon',
            coordinates: item.geometry.coordinates.map(ring =>
              ring.map(coord => [coord[1], coord[0]])
            )
          };
        } else if (item.geometry.type === 'Marker' || item.geometry.type === 'Point') {
          geometry = {
            type: 'Point',
            coordinates: [item.geometry.coordinates[1], item.geometry.coordinates[0]]
          };
        } else if (item.geometry.type === 'LineString') {
          geometry = {
            type: 'LineString',
            coordinates: item.geometry.coordinates.map(coord => [coord[1], coord[0]])
          };
        }
        return { geometry: geometry, properties: item.properties };
      });
      self.postMessage(processedItems);
    }
};
  
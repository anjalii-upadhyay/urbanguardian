// static/simulate.js

// SIMULATION MODE: show 5 random green circles on map load, hover to highlight

const simMap = L.map("simMap").setView([12.9716, 77.5946], 11);

// default tiles
L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
  attribution: "© OpenStreetMap contributors",
}).addTo(simMap);

// load BBMP wards GeoJSON
fetch("https://raw.githubusercontent.com/datameet/Municipal_Spatial_Data/master/Bangalore/BBMP.geojson")
  .then(r => r.json())
  .then(data => {
    const layers = L.geoJSON(data, {
      style: { color:'#000', weight:1 }
    }).addTo(simMap).getLayers();

    // pick 5 random wards
    for (let i = 0; i < 5; i++) {
      const wardLayer = layers[Math.floor(Math.random() * layers.length)];
      const center = wardLayer.getBounds().getCenter();

      // on first hover, draw a green circle that remains
      wardLayer.once('mouseover', () => {
        L.circle(center, {
          radius: 1000,
          color: 'green',
          fillColor: 'green',
          fillOpacity: 0.6
        }).addTo(simMap);
      });
    }
  })
  .catch(err => console.error("Simulation load error:", err));

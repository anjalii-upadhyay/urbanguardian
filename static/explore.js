// static/explore.js

// 1. Initialize map centered on Bangalore
const map = L.map("map").setView([12.9716, 77.5946], 11);

// 2. Add OpenStreetMap base tiles
L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
  attribution: "© OpenStreetMap contributors",
}).addTo(map);

// 3. Fetch BBMP ward boundaries from DataMeet (GeoJSON)
fetch("https://raw.githubusercontent.com/datameet/Municipal_Spatial_Data/master/Bangalore/BBMP.geojson")
  .then(res => {
    if (!res.ok) throw new Error("GeoJSON not found");
    return res.json();
  })
  .then(data => {
    console.log("✅ Loaded wards:", data.features.length, "features");

    // 4. Add GeoJSON layer with black boundaries and no fill
    L.geoJSON(data, {
      style: {
        color: "#000000",  // solid black
        weight: 2,
        fillOpacity: 0
      },
      onEachFeature: function(feature, layer) {
        // Hover effect
        layer.on("mouseover", () => layer.setStyle({ weight: 3 }));
        layer.on("mouseout",  () => layer.setStyle({ weight: 2 }));

        // Click handler: fetch weather + free PM2.5 data
        layer.on("click", async () => {
          const c = layer.getBounds().getCenter();
          const name =
            feature.properties.WARD_NAME ||
            `Ward ${feature.properties.WARD_NO}` ||
            "Unnamed Ward";

          // Call backend for weather & PM2.5
          const resp = await fetch(`/api/explore?lat=${c.lat}&lon=${c.lng}`);
          const d    = await resp.json();

          // Show popup
          layer.bindPopup(`
            🗺️ <b>${name}</b><br/>
            🌡️ ${d.temperature ?? "--"}°C<br/>
            🌬️ ${d.wind        ?? "--"} m/s<br/>
            🌫️ PM₂.₅ ${d.aqi    ?? "--"} µg/m³
          `).openPopup();
        });
      }
    }).addTo(map);
  })
  .catch(err => console.error("Ward-load error:", err));

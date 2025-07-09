// 1) init map
const map = L.map("map").setView([12.9716, 77.5946], 11);
L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
  attribution: "© OpenStreetMap contributors",
}).addTo(map);

// 2) fetch & render wards in BLACK
fetch(
  "https://raw.githubusercontent.com/datameet/Municipal_Spatial_Data/master/Bangalore/BBMP.geojson"
)
  .then((r) => {
    if (!r.ok) throw new Error("GeoJSON not found");
    return r.json();
  })
  .then((geo) => {
    console.log("✅ Sample props:", geo.features[0].properties);

    L.geoJSON(geo, {
      style: {
        color: "black",
        weight: 1,
        fillOpacity: 0,
      },
      onEachFeature: (feature, layer) => {
        // --- HOVER EFFECT ---
        layer.on("mouseover", () => {
          layer.setStyle({ weight: 3, color: "#ff6600" });
        });
        layer.on("mouseout", () => {
          layer.setStyle({ weight: 1, color: "black" });
        });

        // --- CLICK POPUP & CIRCLES ---
        layer.on("click", async () => {
          const c = layer.getBounds().getCenter();
          const p = feature.properties;

          // *** robust ward label ***
          const wardName =
            p.WARD_NAME ||
            p.ward_name ||
            p.WARD_NO ||
            p.ward_no ||
            p.Ward_Id ||
            p.WardID ||
            "Unnamed Ward";

          // fetch realtime data
          const resp = await fetch(`/api/explore?lat=${c.lat}&lon=${c.lng}`);
          const d = await resp.json();

          // popup
          layer
            .bindPopup(`
              🗺️ <b>${wardName}</b><br/>
              🌡️ ${d.temperature ?? "--"}°C<br/>
              🌬️ ${d.wind ?? "--"} m/s<br/>
              🌫️ AQI ${d.aqi ?? "--"}
            `)
            .openPopup();

          // heat-island (temp>35)
          if (d.temperature > 22.6) {
            L.circle([c.lat, c.lng], {
              radius: 500,
              color: "red",
              fillColor: "red",
              fillOpacity: 0.3,
            }).addTo(map);
          }
          // poor-AQI (aqi>150)
          if (d.aqi > 150) {
            L.circle([c.lat, c.lng], {
              radius: 500,
              color: "white",
              fillColor: "white",
              fillOpacity: 0.5,
            }).addTo(map);
          }
        });
      },
    }).addTo(map);
  })
  .catch((err) => console.error("⚠️ Ward-load error:", err));

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
    console.log("✅ Sample properties:", geo.features[0].properties);

    L.geoJSON(geo, {
      style: {
        color: "black",
        weight: 1,
        fillOpacity: 0,        // no fill
      },
      onEachFeature: (feature, layer) => {
        layer.on("click", async () => {
          // 3) grab center & ward-no
          const c = layer.getBounds().getCenter();
          const props = feature.properties;
          // tweak the key name below if your file uses a different property!
          const wardNo =
            props.WARD_NO ||
            props.ward_no ||
            props.Ward_No ||
            props.Ward_ID ||
            "—";
          const name = wardNo !== "—" ? `Ward ${wardNo}` : "Unnamed";

          // 4) realtime API
          const resp = await fetch(
            `/api/explore?lat=${c.lat}&lon=${c.lng}`
          );
          const d = await resp.json();

          // 5) popup
          layer
            .bindPopup(`
              🗺️ <b>${name}</b><br/>
              🌡️ ${d.temperature ?? "--"}°C<br/>
              🌬️ ${d.wind ?? "--"} m/s<br/>
              🌫️ AQI ${d.aqi ?? "--"}
            `)
            .openPopup();

          // 6) heat-island marker (temp > 35°C)
          if (d.temperature > 22.5) {
            L.circle([c.lat, c.lng], {
              radius: 500,
              color: "red",
              fillColor: "red",
              fillOpacity: 0.3,
            }).addTo(map);
          }
          // 7) poor-AQI marker (AQI > 150)
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
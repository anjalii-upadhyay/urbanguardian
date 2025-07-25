// static/explore.js

// 1) Init map
const map = L.map("map").setView([12.9716, 77.5946], 11);

// 2) Satellite basemap
L.tileLayer(
  "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
  {
    attribution:
      "Tiles © Esri — Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, " +
      "Getmapping, Aerogrid, IGN, IGP, UPR-EGP, GIS User Community"
  }
).addTo(map);

// 3) Load & parse CSV
d3.csv(window.APP.CSV_PATH).then(rows => {
  rows.forEach(r => {
    r.raw = +r.avg_temp - +r.baseline_temp;
    r.ward_no = r.ward_no.toString();
  });

  // 4) Compute min/max
  const values = rows.map(r => r.raw);
  const minV = d3.min(values);
  const maxV = d3.max(values);
  const span = maxV - minV || 1;

  // 5) Build lookup: ward → normalized pct (0–100)
  const lookup = {};
  rows.forEach(r => {
    lookup[r.ward_no] = ((r.raw - minV) / span) * 100;
  });

  // 6) Color scale (green → red)
  const colorScale = d3
    .scaleSequential(d3.interpolateRdYlGn)
    .domain([100, 0]); // 0 = green, 100 = red

  // 7) Fetch & draw GeoJSON with anomaly_pct
  fetch("/static/data/wards_with_pct.geojson")
    .then(res => res.json())
    .then(data => {
      L.geoJSON(data, {
        style: feature => {
          const pct = feature.properties.anomaly_pct ?? 0;
          const r = Math.round((pct / 100) * 200);
          const g = Math.round(((100 - pct) / 100) * 200);
          return {
            color: "#000",                   // black boundary
            weight: 1.5,
            fillColor: `rgb(${r},${g},0)`,
            fillOpacity: 0.4
          };
        },
        onEachFeature: (feature, layer) => {
          layer.bindPopup(`
            <b>Ward ${feature.properties.KGISWardNo}</b><br>
            ΔT: ${feature.properties.anomaly_pct.toFixed(1)}%
          `);
          layer.on("mouseover", () => layer.setStyle({ weight: 2 }));
          layer.on("mouseout",  () => layer.setStyle({ weight: 1 }));
        }
      }).addTo(map);

      // 8) Add legend
      const legend = L.control({ position: "bottomright" });
      legend.onAdd = () => {
        const div = L.DomUtil.create("div", "legend");
        div.innerHTML = `
          <b>ΔT Color Scale</b><br>
          <i style="background: ${colorScale(0)}; width:18px; height:10px; display:inline-block;"></i>
            Cool (low ΔT)<br>
          <i style="background: ${colorScale(50)}; width:18px; height:10px; display:inline-block;"></i>
            Medium ΔT<br>
          <i style="background: ${colorScale(100)}; width:18px; height:10px; display:inline-block;"></i>
            Hot (high ΔT)
        `;
        return div;
      };
      legend.addTo(map);
    })
    .catch(console.error);
});

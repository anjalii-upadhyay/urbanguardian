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
    }).catch(console.error);

    // ────────────── HEAT LAYER TOGGLE & LEGEND ────────────────────

    // Capture a reference to the last‐added GeoJSON layer (your heat layer)
    let heatLayer = null;
    map.eachLayer(layer => {
      if (layer instanceof L.GeoJSON) {
        heatLayer = layer;  // assumes this is your ΔT layer
      }
    });

    // 1) Inject toggle control
    const toggleCtrl = L.control({ position: 'topright' });
    toggleCtrl.onAdd = () => {
      const div = L.DomUtil.create('div', 'layer-toggles');
      div.innerHTML = `
        <label style="background:#fff;padding:2px 4px;display:block;">
          <input type="checkbox" id="heat-toggle" checked />
          ${window.APP.LAYER_NAMES.HEAT}
        </label>
        <label style="background:#fff;padding:2px 4px;display:block;">
          <input type="checkbox" id="aqi-toggle" checked />
          ${window.APP.LAYER_NAMES.AQI}
        </label>
      `;
      return div;
    };
    toggleCtrl.addTo(map);

    // 2) Wire up the toggle
    document.getElementById('heat-toggle').addEventListener('change', e => {
      if (!heatLayer) return;
      if (e.target.checked) {
        // restore original fill
        heatLayer.setStyle({ fillOpacity: 0.4 });
      } else {
        // remove fill, keep boundaries
        heatLayer.setStyle({ fillOpacity: 0 });
      }
    });

    document.getElementById('aqi-toggle').addEventListener('change', e => {
      const show = e.target.checked;
      if (show) {
        map.addLayer(aqiLayer);
      } else {
        map.removeLayer(aqiLayer);
      }
    });

    // 3) Re-add your legend so it’s always visible
    const legend = L.control({ position: "bottomright" });
    legend.onAdd = () => {
      const div = L.DomUtil.create("div", "legend");
      div.innerHTML = `
        <b>${window.APP.LAYER_NAMES.HEAT} (ΔT %)</b><br>
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

});

//------------------------ AQI STATION ---------------------
let aqiLayer = L.layerGroup().addTo(map);

d3.csv(window.APP.AQI_CSV_PATH).then(rows => {
  // Step 1: Log to confirm column names
  console.log("AQI CSV loaded:", rows.length, rows);

  // Step 2: Parse with correct column names!
  rows.forEach((r, i) => {
    r.lat = +r.latitude;
    r.lon = +r.longitude;
    r.aqi = +r.AQI;
    if (isNaN(r.lat) || isNaN(r.lon)) {
      console.warn(`⚠️ Row ${i} has bad lat/lon:`, r);
    }
  });

  // Step 3: Show debug for first 5 rows
  rows.slice(0,5).forEach(r => {
    console.log(`Station: ${r.Station}, lat=${r.lat}, lon=${r.lon}, AQI=${r.aqi}`);
  });

  // Step 4: Scaling
  const values = rows.map(r => r.aqi);
  const minA = d3.min(values);
  const maxA = d3.max(values);

  const radiusScale  = d3.scaleLinear().domain([minA, maxA]).range([7, 18]);
  const opacityScale = d3.scaleLinear().domain([minA, maxA]).range([1, 0.2]);  // Best = 1 (opaque), Worst = 0.2 (faint)

  rows.forEach(r => {
    if (isNaN(r.lat) || isNaN(r.lon)) return;
    L.circleMarker([r.lat, r.lon], {
      radius:      radiusScale(r.aqi),
      fillOpacity: opacityScale(r.aqi),
      color:       "#000",
      weight:      1,
      fillColor:   "white"
    })
    .bindPopup(`<b>${r.Station}</b><br>Annual Avg AQI: ${r.aqi}`)
    .addTo(aqiLayer);
  });
}).catch(err => console.error("❌ AQI load failed:", err));

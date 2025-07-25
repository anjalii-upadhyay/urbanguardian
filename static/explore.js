// static/explore.js

import { OPEN_WEATHER_KEY } from "./config.js";

// 1. Initialize the map centered on Bangalore
const map = L.map("map").setView([12.9716, 77.5946], 11);

// 2. Add a satellite basemap (Esri World Imagery)
L.tileLayer(
  "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
  {
    attribution:
      "Tiles © Esri — World_Imagery (Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community)",
    maxZoom: 19,
  }
).addTo(map);

// 3. Prepare the overlay tile layers from OpenWeatherMap
const tempLayer = L.tileLayer(
  `https://tile.openweathermap.org/map/temp_new/{z}/{x}/{y}.png?appid=${OPEN_WEATHER_KEY}`,
  {
    attribution: "🌡️ Heat Island (Temp °C) © OpenWeatherMap",
    opacity: 1,
    maxZoom: 19,
  }
);

const aqiLayer = L.tileLayer(
  `https://tile.openweathermap.org/map/pm2_5/{z}/{x}/{y}.png?appid=${OPEN_WEATHER_KEY}`,
  {
    attribution: "💨 Air Quality (PM2.5) © OpenWeatherMap",
    opacity: 0.5,
    maxZoom: 19,
  }
);

const precipLayer = L.tileLayer(
  `https://tile.openweathermap.org/map/precipitation_new/{z}/{x}/{y}.png?appid=${OPEN_WEATHER_KEY}`,
  {
    attribution: "💧 Precipitation (proxy Water Stress) © OpenWeatherMap",
    opacity: 0.5,
    maxZoom: 19,
  }
);

// 4. Group overlays and add the layer control (expanded by default)
const overlays = {
  "Heat Island (Temp °C)": tempLayer,
  "Air Quality (PM2.5)": aqiLayer,
  "Precipitation (Proxy Water Stress)": precipLayer,
};

L.control
  .layers(
    /* baseLayers = */ null,
    /* overlayLayers = */ overlays,
    {
      collapsed: false,
      position: "topright",
    }
  )
  .addTo(map);

// 5. Show the Heat Island layer by default on load
tempLayer.addTo(map);

// 6. Fetch and draw ward boundaries
fetch(
  "https://raw.githubusercontent.com/datameet/Municipal_Spatial_Data/master/Bangalore/BBMP.geojson"
)
  .then((res) => {
    if (!res.ok) {
      throw new Error("Failed to fetch ward boundaries");
    }
    return res.json();
  })
  .then((geojson) => {
    L.geoJSON(geojson, {
      style: {
        color: "#000",     // black outline
        weight: 1,         // thin line
        fillOpacity: 0,    // no fill
      },
      onEachFeature: (feature, layer) => {
        // subtle highlight on hover
        layer.on("mouseover", () => layer.setStyle({ weight: 2.5 }));
        layer.on("mouseout", () => layer.setStyle({ weight: 1 }));
      },
    }).addTo(map);
  })
  .catch((err) => console.error("Error loading wards geojson:", err));

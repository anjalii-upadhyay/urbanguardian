// static/aqiLayer.js

;(function(){
  // keep a reference so we can remove it later
  let aqiLayerGroup = L.layerGroup();

  // expose a function on window.APP to toggle AQI layer
  window.APP = window.APP || {};
  window.APP.toggleAQILayer = function(show, map) {
    if (!show) {
      map.removeLayer(aqiLayerGroup);
      return;
    }

    // clear out old markers
    aqiLayerGroup.clearLayers();

    // load & draw
    d3.csv(window.APP.AQI_CSV_PATH).then(data => {
        data.forEach(d => {
          d.lat = +d.lat;
          d.lon = +d.lon;
          d.aqi = +d.AQI;
        });

        const vals        = data.map(d => d.aqi),
              minAQI      = d3.min(vals),
              maxAQI      = d3.max(vals),
              radiusScale = d3.scaleLinear().domain([minAQI, maxAQI]).range([6,18]),
              opacityScale= d3.scaleLinear().domain([minAQI, maxAQI]).range([0.4,1.0]);

        data.forEach(d => {
          if (isNaN(d.lat) || isNaN(d.lon)) return;
          const marker = L.circleMarker([d.lat, d.lon], {
            radius:      radiusScale(d.aqi),
            fillOpacity: opacityScale(d.aqi),
            color:       "#000",
            weight:      1,
            fillColor:   d3.interpolateReds((d.aqi - minAQI)/(maxAQI - minAQI))
          })
          .bindPopup(`<b>${d.Station}</b><br>AQI: ${d.aqi}`);
          aqiLayerGroup.addLayer(marker);
        });

        map.addLayer(aqiLayerGroup);
      })
      .catch(err => console.error("❌ AQI load failed:", err));
  };
})();

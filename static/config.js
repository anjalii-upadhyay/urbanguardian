// // export const OPEN_WEATHER_KEY = "123f39e4276ae8f8750e0dc1bf345d83";
// const OPEN_WEATHER_KEY = "123f39e4276ae8f8750e0dc1bf345d83";

window.APP = {
  CSV_PATH:       "/static/data/ward_avgTemp.csv",
  GEOJSON_URL:    "https://raw.githubusercontent.com/datameet/Municipal_Spatial_Data/master/Bangalore/BBMP.geojson",
  AQI_CSV_PATH:   "/static/data/station_annual_avg_all_stations.csv",  // <-- updated
  WATER_CSV:      "/static/data/ward_water.csv",
  LAYER_NAMES: {
    HEAT:  "Heat Island (ΔT)",
    AQI:   "Air Quality (Annual Avg)",
    WATER: "Water Scarcity"
  }
};
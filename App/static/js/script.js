let map;
let currentMarker = null;   // letzter Marker
let currentCircle = null;   // aktueller Kreis

function initMap() {
  map = new google.maps.Map(document.getElementById("map"), {
    zoom: 2,
    center: { lat: 0, lng: 0 },
    mapTypeId: google.maps.MapTypeId.TERRAIN,
    disableDefaultUI: true
  });
}

// Marker hinzufügen / aktualisieren
function addMarker() {
  // Entferne alten Marker und alten Kreis (falls vorhanden)
  if (currentMarker) {
    currentMarker.setMap(null);
  }
  if (currentCircle) {
    currentCircle.setMap(null);
  }

  const latitude = parseFloat(document.getElementById("latitude").value);
  const longitude = parseFloat(document.getElementById("longitude").value);

  if (isNaN(latitude) || isNaN(longitude)) {
    alert("Please enter valid Latitude and Longitude values.");
    return;
  }

  // Wert des Sliders (in km) in Meter umrechnen
  const radiusKm = parseFloat(document.getElementById("radius").value);
  const radiusInMeters = radiusKm * 1000;

  const position = { lat: latitude, lng: longitude };

  // Neuen Marker setzen
  currentMarker = new google.maps.Marker({
    position: position,
    map: map,
    title: "Weather Station"
  });

  // Karte zentrieren und heranzoomen
  map.setCenter(position);
  map.setZoom(10);

  // Kreis zeichnen
  currentCircle = new google.maps.Circle({
    strokeColor: "#FF0000",
    strokeOpacity: 0.8,
    strokeWeight: 2,
    fillColor: "#FF0000",
    fillOpacity: 0.35,
    map: map,
    center: position,
    radius: radiusInMeters
  });
}

// Aktualisiert die Anzeige neben dem Slider
function updateRadiusValue() {
  const radius = document.getElementById("radius").value;
  document.getElementById("radiusValue").textContent = `${radius} km`;
}

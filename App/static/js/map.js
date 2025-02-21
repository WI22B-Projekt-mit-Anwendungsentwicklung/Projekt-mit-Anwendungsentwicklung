let map;
let currentMarker = null;
let currentCircle = null;

async function initMap() {
    map = new google.maps.Map(document.getElementById("map"), {
        zoom: 5,
        center: { lat: 48.132247351247926, lng: 8.677355612809267 },
        mapTypeId: google.maps.MapTypeId.TERRAIN,
        mapId: "WXPlore_Map",
        disableDefaultUI: true
    });
}

function addMarker() {
    const latitude = parseFloat(document.getElementById("latitude").value);
    const longitude = parseFloat(document.getElementById("longitude").value);

    if (isNaN(latitude) || isNaN(longitude)) {
        alert("Please enter valid Latitude and Longitude values.");
        return;
    }

    // Bestehende Marker und Kreise entfernen
    if (currentMarker) {
        currentMarker.map = null;
    }
    if (currentCircle) {
        currentCircle.setMap(null);
    }

    // Radius des Kreises aus dem Sliderwert (in km) umrechnen
    let circleRadius = parseFloat(document.getElementById("radius").value) * 1000;

    const position = { lat: latitude, lng: longitude };

    // Neuen Marker setzen (AdvancedMarkerElement)
    currentMarker = new google.maps.marker.AdvancedMarkerElement({
        map,
        position: position,
        title: "Weather Station"
    });

    // Kreis um den Marker zeichnen
    currentCircle = new google.maps.Circle({
        strokeColor: "#FF0000",
        strokeOpacity: 0.8,
        strokeWeight: 2,
        fillColor: "#FF0000",
        fillOpacity: 0.275,
        map: map,
        center: position,
        radius: circleRadius,
    });

    // Zoom auf den Marker setzen
    map.setCenter(position);
    map.setZoom(8); // Zoom-Level anpassen (je nach gewünschtem Maßstab)

    // Zeitraum validieren
    const yearStart = parseInt(document.getElementById("yearStart").value);
    const yearEnd = parseInt(document.getElementById("yearEnd").value);

    if (!yearStart || !yearEnd || yearStart > yearEnd) {
        alert("Please enter a valid year range.");
        return;
    }
}

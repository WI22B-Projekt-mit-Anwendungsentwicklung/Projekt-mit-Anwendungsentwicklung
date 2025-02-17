// Initialize and add the map
let map;

async function initMap() {
    map = new google.maps.Map(document.getElementById("map"), {
        zoom: 5,
        center: {lat: 48.132247351247926, lng: 8.677355612809267},
        mapTypeId: google.maps.MapTypeId.TERRAIN,
        mapId: "WXPlore_Map",
        disableDefaultUI: true
    });
}


let circleRadius = document.getElementById('radius');
let currentMarker = null;
let currentCircle = null;

function addMarker() {



    const latitude = parseFloat(document.getElementById("latitude").value);
    const longitude = parseFloat(document.getElementById("longitude").value);

    console.log(latitude, longitude)

    if (isNaN(latitude) || isNaN(longitude)) {
        alert("Please enter valid Latitude and Longitude values.");
        return;
    }

    // Wert des Sliders (in km) in Meter umrechnen
    circleRadius = parseFloat(circleRadius.value) * 1000;

    const position = {lat: latitude, lng: longitude};

    // Neuen Marker setzen
    const marker = new google.maps.marker.AdvancedMarkerElement({
        map,
        position: position,
        title: "Weather Station"
    });



    // Kreis zeichnen
    currentCircle = new google.maps.Circle({
        strokeColor: "#FF0000",
        strokeOpacity: 0.8,
        strokeWeight: 2,
        fillColor: "#FF0000",
        fillOpacity: 0.35,
        map: map,
        center: position,
        radius: circleRadius,
    });

    // Zeitraum auslesen
    const yearStart = parseInt(document.getElementById("yearStart").value);
    const yearEnd = parseInt(document.getElementById("yearEnd").value);

    if (!yearStart || !yearEnd || yearStart > yearEnd) {
        alert("Please enter a valid year range.");
        return;
    }

    console.log(`Fetching weather data for years ${yearStart} to ${yearEnd}...`);
}
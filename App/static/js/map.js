let map;
let currentMarker = null;
let currentCircle = null;

async function initMap() {
    map = new google.maps.Map(document.getElementById("map"), {
        zoom: 5,
        center: {lat: 48.132247351247926, lng: 8.677355612809267},
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

    const position = {lat: latitude, lng: longitude};

    // Neuen Marker setzen (AdvancedMarkerElement)
    currentMarker = new google.maps.marker.AdvancedMarkerElement({
        map,
        position: position
    });

    currentMarker.content = document.createElement("div");
    currentMarker.content.innerHTML = `
    <svg width="30" height="30" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
        <path fill="#000000" d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7z"/>
        <circle cx="12" cy="9" r="3" fill="white"/>
    </svg>`;

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

let weatherStationMarkers = []; // Speichert alle Wetterstationsmarker

function addWeatherStations(stations) {
    if (!Array.isArray(stations) || stations.length === 0) {
        console.warn("No stations available to display.");
        return;
    }

    // Alle vorherigen Marker entfernen
    weatherStationMarkers.forEach(marker => marker.map = null);
    weatherStationMarkers = []; // Liste leeren

    stations.forEach(station => {
        const stationId = station[0][0]; // ID der Wetterstation
        const name = station[0][1]; // Name der Wetterstation
        const lat = station[0][2]; // Breitengrad
        const lng = station[0][3]; // Längengrad

        const position = {lat, lng};

        // Container für Marker & Tooltip
        const markerDiv = document.createElement("div");
        markerDiv.classList.add("custom-marker");

        // SVG für einen sichtbaren blauen Marker
        markerDiv.innerHTML = `
            <svg width="30" height="30" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path fill="#D32F2F" d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7z"/>
                <circle cx="12" cy="9" r="3" fill="white"/>
            </svg>`;


        // Tooltip-Element für den Namen
        const tooltip = document.createElement("div");
        tooltip.classList.add("custom-tooltip");
        tooltip.innerText = name;

        // Tooltip an Marker anhängen
        markerDiv.appendChild(tooltip);

        // Neuen Marker erstellen
        const marker = new google.maps.marker.AdvancedMarkerElement({
            map,
            position: position,
            content: markerDiv, // Sichtbarer Marker + Tooltip
            gmpClickable: true,
        });

        // Klick-Event für Scroll-Funktion
        marker.addListener("click", () => {
            scrollToStation(stationId);
        });

        // Marker zur Liste hinzufügen
        weatherStationMarkers.push(marker);
    });
}

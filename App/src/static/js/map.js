let map;
let currentMarker = null;
let currentCircle = null;
let weatherStationMarkers = [];

async function initMap() {
    map = new google.maps.Map(document.getElementById("map"), {
        zoom: 6,
        center: {lat: -53, lng: -70.967},
        mapTypeId: google.maps.MapTypeId.TERRAIN,
        mapId: "WXPlore_Map",
        disableDefaultUI: true
    });
    addRightClickListener();
}

window.onload = function () {
    initMap();
};

function addMarker() {
    const latitude = parseFloat(document.getElementById("latitude").value);
    const longitude = parseFloat(document.getElementById("longitude").value);
    if (isNaN(latitude) || isNaN(longitude)) {
        alert("Please enter valid Latitude and Longitude values.");
        return;
    }
    if (currentMarker) {
        currentMarker.map = null;
    }
    if (currentCircle) {
        currentCircle.setMap(null);
    }
    let circleRadius = parseFloat(document.getElementById("radius").value) * 1000;
    const position = {lat: latitude, lng: longitude};
    currentMarker = new google.maps.marker.AdvancedMarkerElement({
        map,
        position: position,
        content: createCustomMarker("#000000"),
        gmpClickable: true
    });
    currentCircle = new google.maps.Circle({
        strokeColor: "#FF0000",
        strokeOpacity: 0.8,
        strokeWeight: 2,
        fillColor: "#FF0000",
        fillOpacity: 0.275,
        map: map,
        center: position,
        radius: circleRadius,
        clickable: true
    });
    map.setCenter(position);
    map.setZoom(8);
    google.maps.event.addListener(currentCircle, "rightclick", (event) => {
        handleRightClick(event.latLng);
    });
}

function addRightClickListener() {
    map.addListener("rightclick", (event) => {
        handleRightClick(event.latLng);
    });
}

function handleRightClick(latLng) {
    document.getElementById("latitude").value = latLng.lat();
    document.getElementById("longitude").value = latLng.lng();

    clearList();
    clearWeatherStations();
    addMarker();
    getStations();
}

function createCustomMarker(color = "#D32F2F") {
    const markerDiv = document.createElement("div");
    markerDiv.classList.add("custom-marker");
    markerDiv.innerHTML = `
        <svg width="30" height="30" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path fill="${color}" d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7z"/>
            <circle cx="12" cy="9" r="3" fill="white"/>
        </svg>`;
    return markerDiv;
}

function clearWeatherStations() {
    weatherStationMarkers.forEach(marker => marker.map = null);
    weatherStationMarkers = [];
}

function addWeatherStations(stations) {
    clearWeatherStations();
    if (stations.length === 0) {
        console.warn("No stations available to display.");
        return;
    }
    stations.forEach(station => {
        const stationId = station[0][0];
        const name = station[0][1];
        const lat = station[0][2];
        const lng = station[0][3];
        const position = {lat, lng};
        const markerDiv = document.createElement("div");
        markerDiv.classList.add("custom-marker");
        markerDiv.innerHTML = `
            <svg width="30" height="30" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path fill="#D32F2F" d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7z"/>
                <circle cx="12" cy="9" r="3" fill="white"/>
            </svg>`;
        const tooltip = document.createElement("div");
        tooltip.classList.add("custom-tooltip");
        tooltip.innerText = name;
        markerDiv.appendChild(tooltip);
        const marker = new google.maps.marker.AdvancedMarkerElement({
            map,
            position: position,
            content: markerDiv,
            gmpClickable: true,
        });
        marker.addListener("gmp-click", () => {
            scrollToStation(stationId);
        });
        weatherStationMarkers.push(marker);
    });
}

/**
 * =========================================================
 * GLOBAL FUNCTIONS FOR TESTING
 * =========================================================
 */

window.initMap = initMap;
window.addMarker = addMarker;
window.addRightClickListener = addRightClickListener;
window.handleRightClick = handleRightClick;
window.createCustomMarker = createCustomMarker;
window.clearWeatherStations = clearWeatherStations;
window.addWeatherStations = addWeatherStations;

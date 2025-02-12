async function sendStationData() {
    const latitude = document.getElementById("latitude").value;
    const longitude = document.getElementById("longitude").value;
    const radius = document.getElementById("radius").value;
    const yearStart = document.getElementById("yearStart").value;
    const yearEnd = document.getElementById("yearEnd").value;
    const stations = document.getElementById("stations").value;

    const data = {
        latitude: parseFloat(latitude),
        longitude: parseFloat(longitude),
        radius: parseInt(radius),
        yearStart: parseInt(yearStart),
        yearEnd: parseInt(yearEnd),
        // Wenn stations nicht angegeben ist, setze es auf null oder einen Standardwert (z.B. 0)
        stations: stations ? parseInt(stations) : 0  // 'stations' wird entweder als Zahl oder als null übergeben
    };


    try {
        const response = await fetch("http://localhost:8000/submit", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data)
        });

        const result = await response.json();
        console.log("Serverantwort:", result);
    } catch (error) {
        console.error("Fehler beim Senden der Daten:", error);
    }
}

async function sendWeatherData() {
    const stationName = document.getElementById("stationName").value;
    const yearStart = document.getElementById("yearStart").value;
    const yearEnd = document.getElementById("yearEnd").value;

    // Erstellen des Datenobjekts mit den Eingabewerten
    const data = {
        stationName: stationName,  // Stationsname als String
        yearStart: parseInt(yearStart),
        yearEnd: parseInt(yearEnd)
    };

    try {
        const response = await fetch("http://localhost:8000/get_weather_data", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data)
        });

        const result = await response.json();
        console.log("Serverantwort:", result);
    } catch (error) {
        console.error("Fehler beim Senden der Daten:", error);
    }
}


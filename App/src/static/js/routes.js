async function getStations() {
    const latitude = document.getElementById("latitude").value;
    const longitude = document.getElementById("longitude").value;
    const radius = document.getElementById("radius").value;
    const yearStart = document.getElementById("yearStart").value;
    const yearEnd = document.getElementById("yearEnd").value;
    const stations = document.getElementById("stationsInput").value;
    let statioList = document.querySelector("#stationList");
    const data = {
        latitude: parseFloat(latitude),
        longitude: parseFloat(longitude),
        radius: parseInt(radius),
        yearStart: parseInt(yearStart),
        yearEnd: parseInt(yearEnd),
        stations: stations ? parseInt(stations) : -1
    };
    if (isNaN(parseFloat(latitude)) || isNaN(parseFloat(longitude))) {
        return;
    }
    try {
        const response = await fetch("http://localhost:8000/submit", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify(data)
        });
        const result = await response.json();
        let titleSeason = ["Year", "Annual Average Tmin", "Annual Average Tmax", "Spring Tmin", "Spring Tmax",
            "Summer Tmin", "Summer Tmax", "Autumn Tmin", "Autumn Tmax", "Winter Tmin", "Winter Tmax"];
        if (latitude < 0) {
            titleSeason = ["Year", "Annual Average Tmin", "Annual Average Tmax", "Autumn Tmin", "Autumn Tmax",
                "Winter Tmin", "Winter Tmax", "Spring Tmin", "Spring Tmax", "Summer Tmin", "Summer Tmax"];
        }
        if (result.length > 0) {
            statioList.classList.remove("d-none");
            createList(result, yearStart, yearEnd, titleSeason);
            addWeatherStations(result);
        } else {
            alert("No stations found. Please try again.");
            statioList.classList.add("d-none");
        }
    } catch (error) {
        console.error("Fehler beim Senden der Daten:", error);
    }
}

async function getStationData(stationID) {
    const yearStart = document.getElementById("yearStart").value;
    const yearEnd = document.getElementById("yearEnd").value;
    const latitude = document.getElementById("latitude").value;
    const data = {
        stationName: stationID,
        yearStart: parseInt(yearStart),
        yearEnd: parseInt(yearEnd)
    };
    try {
        const response = await fetch("http://localhost:8000/get_weather_data", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify(data)
        });
        const result = await response.json();

        let titleSeason = ["Year", "Annual Average Tmin", "Annual Average Tmax", "Spring Tmin", "Spring Tmax",
            "Summer Tmin", "Summer Tmax", "Autumn Tmin", "Autumn Tmax", "Winter Tmin", "Winter Tmax"];
        if (latitude < 0) {
            titleSeason = ["Year", "Annual Average Tmin", "Annual Average Tmax", "Autumn Tmin", "Autumn Tmax",
                "Winter Tmin", "Winter Tmax", "Spring Tmin", "Spring Tmax", "Summer Tmin", "Summer Tmax"];
        }
        fillTable(result, stationID);
        createChart(result, titleSeason, stationID, latitude);
    } catch (error) {
        console.error("Fehler beim Senden der Daten:", error);
    }
}

/**
 * =========================================================
 * GLOBAL FUNCTIONS FOR TESTING
 * =========================================================
 */

window.getStations = getStations;
window.getStationData = getStationData;

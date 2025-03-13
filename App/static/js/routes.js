export async function getStations() {
    const data = {
        latitude: parseFloat(document.getElementById("latitude").value),
        longitude: parseFloat(document.getElementById("longitude").value),
        radius: parseInt(document.getElementById("radius").value),
        yearStart: parseInt(document.getElementById("yearStart").value),
        yearEnd: parseInt(document.getElementById("yearEnd").value),
        stations: document.getElementById("stationsInput").value ? parseInt(document.getElementById("stationsInput").value) : -1
    };

    if (isNaN(data.latitude) || isNaN(data.longitude)) {
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
        if (data.latitude < 0) {
            titleSeason = ["Year", "Annual Average Tmin", "Annual Average Tmax", "Autumn Tmin", "Autumn Tmax",
                "Winter Tmin", "Winter Tmax", "Spring Tmin", "Spring Tmax", "Summer Tmin", "Summer Tmax"];
        }
        let stationList = document.querySelector("#stationList");
        if (result.length > 0) {
            stationList.classList.remove("d-none");
            createList(result, data.yearStart, data.yearEnd, titleSeason);
            addWeatherStations(result);
        } else {
            alert("No stations found. Please try again.");
            stationList.classList.add("d-none");
        }
    } catch (error) {
        console.error("Fehler beim Senden der Daten:", error);
    }
}

export async function getStationData(stationID) {
    const data = {
        stationName: stationID,
        yearStart: parseInt(document.getElementById("yearStart").value),
        yearEnd: parseInt(document.getElementById("yearEnd").value)
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
        if (parseFloat(document.getElementById("latitude").value) < 0) {
            titleSeason = ["Year", "Annual Average Tmin", "Annual Average Tmax", "Autumn Tmin", "Autumn Tmax",
                "Winter Tmin", "Winter Tmax", "Spring Tmin", "Spring Tmax", "Summer Tmin", "Summer Tmax"];
        }
        fillTable(result, stationID);
        createChart(result, titleSeason, stationID, document.getElementById("latitude").value);
    } catch (error) {
        console.error("Fehler beim Senden der Daten:", error);
    }
}
async function sendData() {
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
        stations: parseInt(stations)
    };

    try {
        const response = await fetch("http://localhost:8000/submit", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data)
        });

        const result = await response.json();
        document.getElementById("responseMessage").textContent = result.message;
        console.log("Serverantwort:", result);
    } catch (error) {
        console.error("Fehler beim Senden der Daten:", error);
    }
}

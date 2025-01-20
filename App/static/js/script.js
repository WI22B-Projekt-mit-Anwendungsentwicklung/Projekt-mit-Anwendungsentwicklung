document.getElementById("submitButton").addEventListener("click", async () => {
    // Nutzerinput abrufen
    const userInput = document.getElementById("userInput").value;

    // Request an die API senden
    if (userInput) {
        try {
            const response = await fetch("/user-input", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ input: userInput })
            });

            if (response.ok) {
                const data = await response.json();
                console.log("Serverantwort:", data);

                // Erfolgsmeldung anzeigen
                document.getElementById("responseMessage").textContent =
                    "Daten erfolgreich gesendet: " + data.data.input;
            } else {
                // Fehler anzeigen
                document.getElementById("responseMessage").textContent =
                    "Fehler beim Senden der Daten.";
            }
        } catch (error) {
            console.error("Fehler:", error);
        }
    } else {
        alert("Bitte gib einen Wert ein!");
    }
});
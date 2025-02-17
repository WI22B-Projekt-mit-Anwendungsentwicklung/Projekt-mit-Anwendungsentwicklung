const toggle = document.getElementById('modeToggle');
const body = document.body;
const header = document.querySelector('header');
const yearStart = document.getElementById('yearStart');
const yearEnd = document.getElementById('yearEnd');
const yearStartSlider = document.getElementById('yearStartSlider');
const yearEndSlider = document.getElementById('yearEndSlider');
const radius = document.getElementById('radius');
const radiusSlider = document.getElementById('radiusSlider');


toggle.addEventListener('change', () => {
    body.classList.toggle('dark-mode', toggle.checked);
});

window.addEventListener('scroll', () => {
    if (window.scrollY > 0) { // Prüfen, ob die Seite gescrollt wurde
        header.classList.add('scrolled'); // Klasse hinzufügen
    } else {
        header.classList.remove('scrolled'); // Klasse entfernen
    }
});

yearStartSlider.addEventListener('input', () => {
    if (parseInt(yearStartSlider.value) > parseInt(yearEndSlider.value)) {
        yearStartSlider.value = yearEndSlider.value;
    }
    yearStart.value = yearStartSlider.value;
});

yearEndSlider.addEventListener('input', () => {
    if (parseInt(yearEndSlider.value) < parseInt(yearStartSlider.value)) {
        yearEndSlider.value = yearStartSlider.value;
    }
    yearEnd.value = yearEndSlider.value;
});

yearStart.addEventListener('input', () => {
    const yearStartValue = parseInt(yearStart.value);
    const yearEndValue = parseInt(yearEnd.value);

    if (yearStartValue > yearEndValue) {
        yearStart.value = yearEndValue; // Setze es auf die gültige Grenze
    }
    yearStartSlider.value = yearStart.value; // Slider entsprechend anpassen
});

yearEnd.addEventListener('input', () => {
    const yearStartValue = parseInt(yearStart.value);
    const yearEndValue = parseInt(yearEnd.value);

    if (yearEndValue < yearStartValue) {
        yearEnd.value = yearStartValue; // Setze es auf die gültige Grenze
    }
    yearEndSlider.value = yearEnd.value; // Slider entsprechend anpassen
});

radiusSlider.addEventListener('input', () => {
    radius.value = radiusSlider.value;
})
radius.addEventListener('input', () => {
    radiusSlider.value = radius.value;
})


const stationBoxes = document.querySelectorAll('.station-box');
const stationsInput = document.getElementById('stationsInput');

stationBoxes.forEach(box => {
    box.addEventListener('click', function () {
        // Entferne die "selected"-Klasse von allen Kästchen
        stationBoxes.forEach(b => b.classList.remove('selected'));

        // Markiere das ausgewählte Kästchen
        this.classList.add('selected');

        // Setze den Wert ins Input-Feld
        stationsInput.value = this.dataset.value;
    });
});

// Falls der Nutzer das Input-Feld manuell nutzt, entferne die Auswahl aus den Kästchen
stationsInput.addEventListener('input', function () {
    stationBoxes.forEach(b => b.classList.remove('selected'));
});

function createList(stations) {
    clearList();

    if (stations.length !== 0) {
        stations.forEach(station => {
            addStation(station); // Station zur Liste hinzufügen
        });
    } else {
        console.log("Keine Einträge vorhanden.");
    }

}

function addStation(station) {
    let liHTMLContent = `
    <div class="list-entry">
        <div class="list-item">
            <p>${station[0][1]}</p>
        </div>
        <div class="list-item">
            <p>${station[0][0]}</p>
        </div>
        <div class="list-item">
            <p>${station[0][2]}</p>
        </div>
        <div class="list-item">
            <p>${station[0][3]}</p>
        </div>
        <div class="list-item">
            <p>${station[1].toFixed(2)} km</p>
        </div>
        <div class="list-item">
            <button onclick="toggleContent('${station[0][0]}'); getStationData('${station[0][0]}')">Aufklappen</button>
        </div>
    </div>
    <div class="station-data-div" id="station-data-div-${station[0][0]}">
        <div class="station-data-content">
            <table class="stations-data-table" id="station-data-table-${station[0][0]}"></table>
        </div>
        <div class="station-data-content" id="station-data-chart-${station[0][0]}"></div>
    </div>
    `
    let newLi = document.createElement("li");
    newLi.innerHTML = liHTMLContent;
    let list = document.getElementById("stationsList");
    list.append(newLi);
}


function clearList() {
    document.getElementById("stationsList").innerHTML = "";
}


function toggleContent(index) {
    let id = `station-data-div-${index}`;
    console.log(id);
    let content = document.getElementById(`station-data-div-${index}`);
    content.classList.toggle('open');
}

function createTable(data, index, yearStart, yearEnd) {
    let table = document.getElementById(`station-data-table-${index}`);

    // Pruefen, ob Daten vorhanden sind
    if (!data || data.length === 0 || !table) {
        console.warn(`Keine Daten oder Ziel-Tabelle für Index ${index} gefunden.`);
        return;
    }

    // Tabelle zurücksetzen
    table.innerHTML = '';

    // Alle Jahre im Bereich sammeln
    let years = [];
    for (let year = yearStart; year <= yearEnd; year++) {
        years.push(year);
    }

    // Erstelle Header-Row (mit "Jahr" als erster Spalte)
    let headerRow = document.createElement('tr');
    let yearHeader = document.createElement('th');
    yearHeader.textContent = 'Jahr'; // Erste Spalte: "Jahr"
    headerRow.appendChild(yearHeader);

    // Dynamischer Header für Spalten
    for (let i = 0; i < data.length; i++) {
        let th = document.createElement('th');
        th.textContent = `Spalte ${i + 1}`; // Beschriftung: Spalte 1, Spalte 2, ...
        headerRow.appendChild(th);
    }
    table.appendChild(headerRow);

    // Erstellen der Zeilen: Jahr-basierte Iteration
    for (let i = 0; i < years.length; i++) {
        let row = document.createElement('tr');

        // Erstelle die Spalte für das Jahr
        let yearCell = document.createElement('td');
        yearCell.textContent = years[i];
        row.appendChild(yearCell);

        // Jede Datenspalte für das aktuelle Jahr prüfen
        for (let colIndex = 0; colIndex < data.length; colIndex++) {
            let cell = document.createElement('td');
            // Hole den Wert, falls für das Jahr ein Wert in dieser Spalte vorliegt
            if (data[colIndex][i] !== undefined) {
                cell.textContent = data[colIndex][i]; // Wert setzen
            } else {
                cell.textContent = ''; // Leer lassen, wenn kein Wert vorhanden ist
            }
            row.appendChild(cell);
        }

        // Zeile zur Tabelle hinzufügen
        table.appendChild(row);
    }
}
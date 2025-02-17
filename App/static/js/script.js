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
    console.log(stations);
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
            <p>Test</p>
        </div>
        <div class="list-item">
            <p>${station.stationId}</p>
        </div>
        <div class="list-item">
            <p>${station.latitude}</p>
        </div>
        <div class="list-item">
            <p>${station.longitude}</p>
        </div>
        <div class="list-item">
            <button onclick="toggleContent(${station.stationId})">Aufklappen</button>
        </div>
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
    let content = document.querySelectorAll('.content')[index];
    content.classList.toggle('open');
}






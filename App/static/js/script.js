const toggle = document.getElementById('modeToggle');
const body = document.body;
const header = document.querySelector('header');
const yearStart = document.getElementById('yearStart');
const yearEnd = document.getElementById('yearEnd');
const yearStartSlider = document.getElementById('yearStartSlider');
const yearEndSlider = document.getElementById('yearEndSlider');
const radius = document.getElementById('radius');
const radiusSlider = document.getElementById('radiusSlider');
const stationBoxes = document.querySelectorAll('.station-box');
const stationsInput = document.getElementById('stationsInput');
const logo = document.getElementById("logo");
const lightLogo = logo.getAttribute("data-light");
const darkLogo = logo.getAttribute("data-dark");

toggle.addEventListener("change", () => {
    body.classList.toggle("dark-mode", toggle.checked);
    logo.src = toggle.checked ? darkLogo : lightLogo;
});

window.addEventListener('scroll', () => {
    if (window.scrollY > 0) {
        header.classList.add('scrolled');
    } else {
        header.classList.remove('scrolled');
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

yearStart.addEventListener('blur', () => {
    validateInput(yearStart, 1763, 2024, "Start year");
    if (isNaN(parseInt(yearStart.value)) || !/^-?\d{4}$/.test(yearStart.value)) {
        alert("Start year must be a four-digit integer.");
        yearStart.value = 1763;
    } else if (parseInt(yearStart.value) > parseInt(yearEnd.value)) {
        alert("The start year cannot be greater than the end year.");
        yearStart.value = 1763;
    }
    yearStartSlider.value = yearStart.value;
});

yearEnd.addEventListener('blur', () => {
    validateInput(yearEnd, 1763, 2024, "End year");
    if (isNaN(parseInt(yearEnd.value)) || !/^-?\d{4}$/.test(yearEnd.value)) {
        alert("End year must be a four-digit integer.");
        yearEnd.value = 2024;
    } else if (parseInt(yearEnd.value) < parseInt(yearStart.value)) {
        alert("The end year cannot be greater than the start year.");
        yearEnd.value = 2024;
    }
    yearEndSlider.value = yearEnd.value;
});

radiusSlider.addEventListener('input', () => {
    radius.value = radiusSlider.value;
});

radius.addEventListener('blur', () => {
    validateInput(radius, 1, 100, "Radius");
    if (isNaN(parseInt(radius.value)) || !/^\d+$/.test(radius.value)) {
        alert("Please enter a valid integer for radius.");
        radius.value = 50;
    }
    radiusSlider.value = radius.value;
});

stationsInput.addEventListener("blur", function () {
    let value = this.value.trim();
    if (!/^\d+$/.test(value) || parseInt(value) <= 0) {
        alert("The number of stations must be a positive integer.");
        this.value = null;
    }
});

function validateInput(input, min, max, message) {
    let value = parseInt(input.value);
    if (isNaN(value)) {
        return;
    }
    if (value < min) {
        alert(`${message} cannot be less than ${min}.`);
        input.value = min;
    } else if (value > max) {
        alert(`${message} cannot be more than ${max}.`);
        input.value = max;
    }
}

stationBoxes.forEach(box => {
    box.addEventListener('click', function () {
        stationBoxes.forEach(b => b.classList.remove('selected'));
        this.classList.add('selected');
        stationsInput.value = this.dataset.value;
    });
});

stationsInput.addEventListener('input', function () {
    stationBoxes.forEach(b => b.classList.remove('selected'));
});

function createList(stations, yearStart, yearEnd, titleSeason) {
    clearList();
    if (stations.length !== 0) {
        stations.forEach(station => {
            addStation(station, yearStart, yearEnd, titleSeason);
        });
    } else {
        console.log("Keine Einträge vorhanden.");
    }
}

function addStation(station, yearStart, yearEnd, titleSeason) {
    let tableHeaderHTML = '<tr>' + titleSeason.map(header => `<th>${header}</th>`).join('') + '</tr>';
    let tableRowsHTML = '';
    for (let year = yearStart; year <= yearEnd; year++) {
        tableRowsHTML += `<tr><td>${year}</td>` + '<td></td>'.repeat(10) + '</tr>';
    }
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
        <div class="list-item arrow-div">
            <img src="/static/arrow.png" class="toggle-arrow" id="arrow-${station[0][0]}" 
                onclick="toggleContent('${station[0][0]}'); getStationData('${station[0][0]}')" />
        </div>
    </div>
    <div class="station-data-div" id="station-data-div-${station[0][0]}">
        <div class="station-data-content table-div">
            <table class="stations-data-table" id="station-data-table-${station[0][0]}">
                ${tableHeaderHTML}
                ${tableRowsHTML}
            </table>
        </div>
        <div class="station-data-content chart-div">
            <canvas id="station-data-chart-${station[0][0]}"></canvas>
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


function toggleContent(stationID) {
    let content = document.getElementById(`station-data-div-${stationID}`);
    let arrow = document.getElementById(`arrow-${stationID}`);
    content.classList.toggle('open');
    arrow.classList.toggle('rotated');
}


function fillTable(data, stationID) {
    let table = document.getElementById(`station-data-table-${stationID}`);
    if (!table) return;

    let rows = table.getElementsByTagName("tr");
    let yearIndexMap = {};

    for (let i = 1; i < rows.length; i++) {
        let year = parseInt(rows[i].cells[0].textContent);
        yearIndexMap[year] = i;
    }
    for (let col = 0; col < data.length; col++) {
        let columnData = data[col];
        for (let i = 0; i < columnData.length; i++) {
            let [year, value] = columnData[i];
            if (yearIndexMap.hasOwnProperty(year)) {
                let rowIndex = yearIndexMap[year];
                rows[rowIndex].cells[col + 1].textContent = value.toFixed(2);
            }
        }
    }
}

const colorMap = {};
const predefinedColors = [
    'rgb(255, 99, 132)', 'rgb(54, 162, 235)', 'rgb(255, 206, 86)',
    'rgb(75, 192, 192)', 'rgb(153, 102, 255)', 'rgb(255, 159, 64)',
    'rgb(199, 199, 199)', 'rgb(83, 102, 255)', 'rgb(255, 99, 64)', 'rgb(99, 255, 132)'
];
const charts = {};

function createChart(data, titleSeason, stationID) {
    let ctx = document.getElementById(`station-data-chart-${stationID}`).getContext('2d');
    if (charts[stationID]) {
        charts[stationID].destroy();
    }
    let datasets = data.map((column, index) => {
        let titleIndex = index + 1;
        if (!colorMap[titleSeason[titleIndex]]) {
            colorMap[titleSeason[titleIndex]] = predefinedColors[titleIndex % predefinedColors.length];
        }
        return {
            label: titleSeason[titleIndex],
            data: column.map(entry => ({ x: entry[0], y: entry[1] })),
            fill: false,
            borderColor: colorMap[titleSeason[titleIndex]],
            tension: 0.1
        };
    });
    charts[stationID] = new Chart(ctx, {
        type: 'line',
        data: {
            datasets: datasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    type: 'linear',
                    position: 'bottom',
                    title: {
                        display: true,
                        text: 'Year'
                    },
                    ticks: {
                        callback: function (value) {
                            return parseInt(value, 10);
                        }
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: 'Temperature (°C)'
                    }
                }
            },
            plugins: {
                tooltip: {
                    callbacks: {
                        title: function (tooltipItems) {
                            return parseInt(tooltipItems[0].parsed.x, 10);
                        },
                        label: function (tooltipItem) {
                            let value = tooltipItem.parsed.y.toFixed(2);
                            return `${tooltipItem.dataset.label}: ${value} °C`;
                        }
                    }
                }
            }
        }
    });
}



function scrollToStation(stationID) {
    let content = document.getElementById(`station-data-div-${stationID}`);
    if (content) {
        if (!content.classList.contains("open")) {
            toggleContent(stationID);
            getStationData(stationID);
        }
        content.scrollIntoView({ behavior: "smooth", block: "start" });
    }
}




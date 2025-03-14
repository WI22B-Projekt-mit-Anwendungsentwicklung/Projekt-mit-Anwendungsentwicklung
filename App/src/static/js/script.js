document.getElementById('modeToggle').addEventListener("change", () => {
    document.body.classList.toggle("dark-mode", document.getElementById('modeToggle').checked);
    document.getElementById("logo").src = document.getElementById('modeToggle').checked ? document.getElementById("logo").getAttribute("data-dark") : document.getElementById("logo").getAttribute("data-light");
});

window.addEventListener('scroll', () => {
    if (window.scrollY > 0) {
        document.querySelector('header').classList.add('scrolled');
    } else {
        document.querySelector('header').classList.remove('scrolled');
    }
});

document.getElementById('yearStartSlider').addEventListener('input', () => {
    if (parseInt(document.getElementById('yearStartSlider').value) > parseInt(document.getElementById('yearEndSlider').value)) {
        document.getElementById('yearStartSlider').value = document.getElementById('yearEndSlider').value;
    }
    document.getElementById('yearStart').value = document.getElementById('yearStartSlider').value;
});

document.getElementById('yearEndSlider').addEventListener('input', () => {
    if (parseInt(document.getElementById('yearEndSlider').value) < parseInt(document.getElementById('yearStartSlider').value)) {
        document.getElementById('yearEndSlider').value = document.getElementById('yearStartSlider').value;
    }
    document.getElementById('yearEnd').value = document.getElementById('yearEndSlider').value;
});

document.getElementById('yearStart').addEventListener('blur', () => {
    validateInput(document.getElementById('yearStart'), 1763, 2024, "Start year");
    if (isNaN(parseInt(document.getElementById('yearStart').value)) || !/^-?\d{4}$/.test(document.getElementById('yearStart').value)) {
        alert("Start year must be a four-digit integer.");
        document.getElementById('yearStart').value = 1763;
    } else if (parseInt(document.getElementById('yearStart').value) > parseInt(document.getElementById('yearEnd').value)) {
        alert("The start year cannot be greater than the end year.");
        document.getElementById('yearStart').value = 1763;
    }
    document.getElementById('yearStartSlider').value = document.getElementById('yearStart').value;
});

document.getElementById('yearEnd').addEventListener('blur', () => {
    validateInput(document.getElementById('yearEnd'), 1763, 2024, "End year");
    if (isNaN(parseInt(document.getElementById('yearEnd').value)) || !/^-?\d{4}$/.test(document.getElementById('yearEnd').value)) {
        alert("End year must be a four-digit integer.");
        document.getElementById('yearEnd').value = 2024;
    } else if (parseInt(document.getElementById('yearEnd').value) < parseInt(document.getElementById('yearStart').value)) {
        alert("The end year cannot be greater than the start year.");
        document.getElementById('yearEnd').value = 2024;
    }
    document.getElementById('yearEndSlider').value = document.getElementById('yearEnd').value;
});

document.getElementById('radiusSlider').addEventListener('input', () => {
    document.getElementById('radius').value = document.getElementById('radiusSlider').value;
});

document.getElementById('radius').addEventListener('blur', () => {
    validateInput(document.getElementById('radius'), 1, 100, "Radius");
    if (isNaN(parseInt(document.getElementById('radius').value)) || !/^\d+$/.test(document.getElementById('radius').value)) {
        alert("Please enter a valid integer for radius.");
        document.getElementById('radius').value = 50;
    }
    document.getElementById('radiusSlider').value = document.getElementById('radius').value;
});

document.getElementById('stationsInput').addEventListener("blur", function () {
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

document.querySelectorAll('.station-box').forEach(box => {
    box.addEventListener('click', function () {
        document.querySelectorAll('.station-box').forEach(b => b.classList.remove('selected'));
        this.classList.add('selected');
        document.getElementById('stationsInput').value = this.dataset.value;
    });
});

document.getElementById('stationsInput').addEventListener('input', function () {
    document.querySelectorAll('.station-box').forEach(b => b.classList.remove('selected'));
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
                <p>${station[1].toFixed(1)} km</p>
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
                rows[rowIndex].cells[col + 1].textContent = value.toFixed(1);
            }
        }
    }
}

const colorMap = {};
const predefinedColorsNorth = [
    'rgb(191,191,191)', 'rgb(0,0,255)', 'rgb(255,0,0)',
    'rgb(61,145,1)', 'rgb(173,255,139)', 'rgb(255,124,0)',
    'rgb(255,154,82)', 'rgb(112,53,0)', 'rgb(124,99,84)', 'rgb(131,131,131)'
];
const predefinedColorsSouth = [
    'rgb(255,154,82)', 'rgb(0,0,255)', 'rgb(255,0,0)',
    'rgb(112,53,0)', 'rgb(124,99,84)', 'rgb(131,131,131)',
    'rgb(191,191,191)', 'rgb(61,145,1)', 'rgb(173,255,139)', 'rgb(255,124,0)'
]
const charts = {};

function createChart(data, titleSeason, stationID, latitude) {
    let predefinedColors = predefinedColorsNorth;
    if (latitude < 0) {
        predefinedColors = predefinedColorsSouth;
    }
    let ctx = document.getElementById(`station-data-chart-${stationID}`).getContext('2d');
    if (charts[stationID]) {
        charts[stationID].destroy();
    }

    let allYears = new Set();
    data.forEach(column => column.forEach(entry => allYears.add(entry[0])));
    let minYear = Math.min(...allYears);
    let maxYear = Math.max(...allYears);

    let fullYearRange = Array.from({length: maxYear - minYear + 1}, (_, i) => minYear + i);

    let datasets = data.map((column, index) => {
        let titleIndex = index + 1;
        if (!colorMap[titleSeason[titleIndex]]) {
            colorMap[titleSeason[titleIndex]] = predefinedColors[titleIndex % predefinedColors.length];
        }

        let dataMap = new Map(column.map(entry => [entry[0], entry[1]]));

        let filledData = fullYearRange.map(year => ({
            x: year,
            y: dataMap.has(year) ? dataMap.get(year) : null
        }));

        return {
            label: titleSeason[titleIndex],
            data: filledData,
            fill: false,
            borderColor: colorMap[titleSeason[titleIndex]],
            tension: 0.1,
            spanGaps: false,
            hidden: index >= 2,
            segment: {
                borderDash: ctx => ctx.p0.skip || ctx.p1.skip ? [5, 5] : undefined
            }
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
                            let value = tooltipItem.parsed.y !== null ? tooltipItem.parsed.y.toFixed(1) : 'No Data';
                            return `${tooltipItem.dataset.label}: ${value} °C`;
                        }
                    }
                }
            }
        }
    });
}

function scrollToStation(stationID) {
    if (document.getElementById(`station-data-div-${stationID}`)) {
        if (!document.getElementById(`station-data-div-${stationID}`).classList.contains("open")) {
            toggleContent(stationID);
            getStationData(stationID);
        }
        document.getElementById(`station-data-div-${stationID}`).scrollIntoView({behavior: "smooth", block: "start"});
    }
}

/**
 * =========================================================
 * GLOBAL FUNCTIONS FOR TESTING
 * =========================================================
 */

window.validateInput = validateInput;
window.clearList = clearList;
window.createList = createList;
window.fillTable = fillTable;
window.addStation = addStation;
window.toggleContent = toggleContent;
window.createChart = createChart;
window.scrollToStation = scrollToStation;


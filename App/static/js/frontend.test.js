/**
 * @jest-environment jsdom
 */

/**
 * =========================================================
 * GLOBAL SECTION
 * =========================================================
 */
beforeAll(() => {
  console.log("GLOBAL beforeAll(): Setup for all frontend tests.");
});

/**
 * =========================================================
 * TESTS FOR .JS
 * -> map.js
 * -> routes.js
 * -> script.js
 * =========================================================
 */


// ----------------------------------
// Tests for map.js
// ----------------------------------


import {
  initMap,
  addMarker,
  addRightClickListener,
  addWeatherStations
} from "./map.js";

describe("Tests for map.js", () => {
  let originalAlert;
  let latitudeInput, longitudeInput, radiusInput;

  beforeAll(() => {
    global.google = {
      maps: {
        Map: jest.fn().mockImplementation(() => ({
          setCenter: jest.fn(),
          setZoom: jest.fn(),
          addListener: jest.fn()
        })),
        Circle: jest.fn().mockImplementation(() => ({
          setMap: jest.fn()
        })),
        event: {
          addListener: jest.fn()
        },
        marker: {
          AdvancedMarkerElement: jest.fn().mockImplementation(() => ({
            map: null,
            addListener: jest.fn()
          }))
        },
        MapTypeId: {
          TERRAIN: "TERRAIN"
        }
      }
    };
    global.console.warn = jest.fn();
  });

  beforeEach(() => {
    // DOM vorbereiten
    document.body.innerHTML = `
      <input id="latitude" value="0" />
      <input id="longitude" value="0" />
      <input id="radius" value="50" />
      <div id="map"></div>
    `;

    originalAlert = global.alert;
    global.alert = jest.fn();
    global.clearList = jest.fn();
    global.getStations = jest.fn();
    global.scrollToStation = jest.fn();
    initMap();
  });

  afterEach(() => {
    global.alert = originalAlert;
    jest.clearAllMocks();
  });

  describe("addMarker()", () => {
    test("should alert if lat/long are invalid", () => {
      document.getElementById("latitude").value = "abc";
      document.getElementById("longitude").value = "def";
      addMarker();
      expect(global.alert).toHaveBeenCalledWith("Please enter valid Latitude and Longitude values.");
    });

    test("should create currentMarker/currentCircle with valid lat/long", () => {
      document.getElementById("latitude").value = "10";
      document.getElementById("longitude").value = "20";
      document.getElementById("radius").value = "5";

      addMarker();

      expect(global.google.maps.marker.AdvancedMarkerElement).toHaveBeenCalledTimes(1);
      expect(global.google.maps.Circle).toHaveBeenCalledWith(
        expect.objectContaining({
          center: { lat: 10, lng: 20 },
          radius: 5000 // 5 * 1000
        })
      );

      const mockMapInstance = global.google.maps.Map.mock.results[0].value;
      expect(mockMapInstance.setCenter).toHaveBeenCalledWith({ lat: 10, lng: 20 });
      expect(mockMapInstance.setZoom).toHaveBeenCalledWith(8);
    });
  });

  describe("addRightClickListener()", () => {
    test("attaches a 'rightclick' listener", () => {
      addRightClickListener();
      const mockMapInstance = global.google.maps.Map.mock.results[0].value;
      expect(mockMapInstance.addListener).toHaveBeenCalledWith(
        "rightclick",
        expect.any(Function)
      );
    });
  });

  describe("addWeatherStations()", () => {
    test("warns if stations.length === 0", () => {
      addWeatherStations([]);
      expect(global.console.warn).toHaveBeenCalledWith("No stations available to display.");
    });

    test("creates new markers for each station", () => {
      const stations = [
        [[1, "StationOne", 10, 20], 123],
        [[2, "StationTwo", 30, 40], 456],
      ];
      addWeatherStations(stations);
      expect(global.google.maps.marker.AdvancedMarkerElement).toHaveBeenCalledTimes(2);
      const mockMarker = global.google.maps.marker.AdvancedMarkerElement.mock.results[0].value;
      expect(mockMarker.addListener).toHaveBeenCalledWith("gmp-click", expect.any(Function));
    });
  });
});


// ----------------------------------
// Tests for routes.js
// ----------------------------------


import { getStations, getStationData } from "./routes.js";

describe("Tests for routes.js", () => {
  let originalFetch;
  let originalAlert;

  beforeAll(() => {
    originalFetch = global.fetch;
    global.fetch = jest.fn();
    originalAlert = global.alert;
    global.alert = jest.fn();
    global.console.error = jest.fn();
  });

  beforeEach(() => {
    // Prepare DOM
    document.body.innerHTML = `
      <input id="latitude" value="0" />
      <input id="longitude" value="0" />
      <input id="radius" value="50" />
      <input id="yearStart" value="2000" />
      <input id="yearEnd" value="2020" />
      <input id="stationsInput" value="3" />
      <div id="stationList" class="d-none"></div>
    `;

    global.createList = jest.fn();
    global.addWeatherStations = jest.fn();
    global.fillTable = jest.fn();
    global.createChart = jest.fn();
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  afterAll(() => {
    global.fetch = originalFetch;
    global.alert = originalAlert;
  });

  // getStations TESTS
  describe("getStations()", () => {
    test("Should return early if lat/long are invalid (no fetch call)", async () => {
      document.getElementById("latitude").value = "abc";
      document.getElementById("longitude").value = "xyz";
      await getStations();
      expect(global.fetch).not.toHaveBeenCalled();
    });

    test("Should fetch with correct body, show alert if result is empty", async () => {
      document.getElementById("latitude").value = "45";
      document.getElementById("longitude").value = "9";
      global.fetch.mockResolvedValue({
        json: async () => []
      });

      await getStations();
      expect(global.fetch).toHaveBeenCalledWith("http://localhost:8000/submit", expect.any(Object));
      const fetchCall = global.fetch.mock.calls[0][1]; // [url, options]
      const bodyData = JSON.parse(fetchCall.body);
      expect(bodyData).toEqual({
        latitude: 45,
        longitude: 9,
        radius: 50,
        yearStart: 2000,
        yearEnd: 2020,
        stations: 3
      });

      expect(global.alert).toHaveBeenCalledWith("No stations found. Please try again.");
      const stationListDiv = document.getElementById("stationList");
      expect(stationListDiv.classList.contains("d-none")).toBe(true);
      expect(global.createList).not.toHaveBeenCalled();
      expect(global.addWeatherStations).not.toHaveBeenCalled();
    });

    test("Should remove d-none, call createList + addWeatherStations if result has data", async () => {
      document.getElementById("latitude").value = "45";
      document.getElementById("longitude").value = "9";
      const mockResult = [[["id1", "Station1", 45, 9], 123]];
      global.fetch.mockResolvedValue({
        json: async () => mockResult
      });

      await getStations();
      expect(global.alert).not.toHaveBeenCalled();
      const stationListDiv = document.getElementById("stationList");
      expect(stationListDiv.classList.contains("d-none")).toBe(false);
      expect(global.createList).toHaveBeenCalledWith(mockResult, "2000", "2020", expect.any(Array));
      expect(global.addWeatherStations).toHaveBeenCalledWith(mockResult);
    });

    test("Should use alternative titleSeason if latitude < 0", async () => {
      document.getElementById("latitude").value = "-23";
      document.getElementById("longitude").value = "9";

      // Test-Data
      global.fetch.mockResolvedValue({
        json: async () => [[["id2", "Station2", -23, 9], 123]]
      });

      await getStations();
      const secondArg = global.createList.mock.calls[0][3];
      expect(secondArg).toEqual([
        "Year",
        "Annual Average Tmin",
        "Annual Average Tmax",
        "Autumn Tmin",
        "Autumn Tmax",
        "Winter Tmin",
        "Winter Tmax",
        "Spring Tmin",
        "Spring Tmax",
        "Summer Tmin",
        "Summer Tmax"
      ]);
    });

    test("Should console.error if fetch fails", async () => {
      document.getElementById("latitude").value = "45";
      document.getElementById("longitude").value = "9";
      global.fetch.mockRejectedValue(new Error("network error"));
      await getStations();
      expect(global.console.error).toHaveBeenCalledWith(
        "Fehler beim Senden der Daten:",
        expect.any(Error)
      );
    });
  });

  // getStationData TESTS
  describe("getStationData()", () => {
    test("Should call fillTable + createChart on success", async () => {
      // yearStart=2000, yearEnd=2020, lat=0 => normal Seasons
      document.getElementById("latitude").value = "0";

      // Test-Data
      const mockResult = [["2000", 10], ["2001", 12]];
      global.fetch.mockResolvedValue({
        json: async () => mockResult
      });

      await getStationData("idX");
      expect(global.fetch).toHaveBeenCalledWith("http://localhost:8000/get_weather_data", expect.any(Object));
      expect(global.fillTable).toHaveBeenCalledWith(mockResult, "idX");
      expect(global.createChart).toHaveBeenCalledWith(mockResult, expect.any(Array), "idX", "0");
    });

    test("Should use alternative seasons if latitude < 0", async () => {
      document.getElementById("latitude").value = "-12"; // lat < 0
      global.fetch.mockResolvedValue({ json: async () => [] });
      await getStationData("idY");
      const seasonArray = global.createChart.mock.calls[0][1];
      expect(seasonArray).toEqual([
        "Year",
        "Annual Average Tmin",
        "Annual Average Tmax",
        "Autumn Tmin",
        "Autumn Tmax",
        "Winter Tmin",
        "Winter Tmax",
        "Spring Tmin",
        "Spring Tmax",
        "Summer Tmin",
        "Summer Tmax"
      ]);
    });

    test("Should console.error on fetch error", async () => {
      global.fetch.mockRejectedValue(new Error("server error"));
      await getStationData("idZ");
      expect(global.console.error).toHaveBeenCalledWith(
        "Fehler beim Senden der Daten:",
        expect.any(Error)
      );
    });
  });
});


// ----------------------------------
// Tests for script.js
// ----------------------------------

import {
  validateInput,
  clearList,
  createList,
  addStation,
  toggleContent,
  fillTable,
  createChart,
  scrollToStation
} from "./script.js";

describe("Tests for script.js logic functions", () => {
  beforeEach(() => {
    // Vollständige DOM-Struktur, die alle Elemente enthält, die der Code erwartet.
    document.body.innerHTML = `
      <header></header>
      <input type="checkbox" id="modeToggle" />
      <img id="logo" data-light="light-logo.png" data-dark="dark-logo.png" />
      
      <!-- Year inputs + sliders -->
      <input id="yearStart" value="2000" />
      <input id="yearEnd" value="2020" />
      <input id="yearStartSlider" type="range" min="1763" max="3000" value="2000" />
      <input id="yearEndSlider" type="range" min="1763" max="3000" value="2020" />
      
      <!-- Radius -->
      <input id="radius" value="50" />
      <input id="radiusSlider" type="range" min="1" max="100" value="50" />
      
      <!-- Station Boxes & Input -->
      <div class="station-box" data-value="5"></div>
      <div class="station-box" data-value="10"></div>
      <input id="stationsInput" />
      
      <!-- Container für List & Table -->
      <ul id="stationsList"></ul>
      
      <!-- Canvas für Chart -->
      <canvas id="station-data-chart-test"></canvas>
      
      <!-- Elemente für toggleContent & scrollToStation -->
      <div id="station-data-div-test"></div>
      <img id="arrow-test" class="toggle-arrow" />
    `;
    // Initialisiere logo
    const logo = document.getElementById("logo");
    logo.src = logo.getAttribute("data-light");

    // Mock global.alert und console.log, um Alerts abzufangen und Log-Ausgaben zu testen.
    global.alert = jest.fn();
    global.console.log = jest.fn();
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  // ----------------------------------
  // Dark Mode & Scroll Logic
  // ----------------------------------
  describe("Dark Mode & Scroll Logic", () => {
    test("Toggle changes dark-mode class and switches logo src", () => {
      const toggle = document.getElementById("modeToggle");
      const body = document.body;
      const logo = document.getElementById("logo");
      // Anfangszustand
      expect(body.classList.contains("dark-mode")).toBe(false);
      expect(logo.src).toContain("light-logo.png");

      // Toggle einschalten
      toggle.checked = true;
      toggle.dispatchEvent(new Event("change"));
      expect(body.classList.contains("dark-mode")).toBe(true);
      expect(logo.src).toContain("dark-logo.png");

      // Toggle ausschalten
      toggle.checked = false;
      toggle.dispatchEvent(new Event("change"));
      expect(body.classList.contains("dark-mode")).toBe(false);
      expect(logo.src).toContain("light-logo.png");
    });

    test("Scroll event adds 'scrolled' class when scrollY > 0 and removes it when scrollY is 0", () => {
      const header = document.querySelector("header");
      // Simuliere scrollY > 0
      Object.defineProperty(window, "scrollY", { value: 100, writable: true });
      window.dispatchEvent(new Event("scroll"));
      expect(header.classList.contains("scrolled")).toBe(true);
      // Simuliere scrollY = 0
      Object.defineProperty(window, "scrollY", { value: 0, writable: true });
      window.dispatchEvent(new Event("scroll"));
      expect(header.classList.contains("scrolled")).toBe(false);
    });
  });

  // ----------------------------------
  // Year Sliders & Blur Logic
  // ----------------------------------
  describe("Year Sliders & Blur Logic", () => {
    test("yearStartSlider input synchronizes yearStart value", () => {
      const yearStart = document.getElementById("yearStart");
      const yearStartSlider = document.getElementById("yearStartSlider");
      yearStartSlider.value = "2025";
      yearStartSlider.dispatchEvent(new Event("input"));
      expect(yearStart.value).toBe("2025");
    });

    test("yearEndSlider input synchronizes yearEnd value", () => {
      const yearEnd = document.getElementById("yearEnd");
      const yearEndSlider = document.getElementById("yearEndSlider");
      yearEndSlider.value = "2030";
      yearEndSlider.dispatchEvent(new Event("input"));
      expect(yearEnd.value).toBe("2030");
    });

    test("Blur on yearStart with valid input does not trigger alert", () => {
      const yearStart = document.getElementById("yearStart");
      const yearEnd = document.getElementById("yearEnd");
      const yearStartSlider = document.getElementById("yearStartSlider");
      // Setze einen gültigen Wert, der innerhalb des Bereichs liegt und kleiner als yearEnd
      yearStart.value = "1990";
      yearEnd.value = "2000";
      yearStart.dispatchEvent(new Event("blur"));
      expect(global.alert).not.toHaveBeenCalled();
      expect(yearStartSlider.value).toBe("1990");
    });

    test("Blur on yearStart outside range triggers alerts and resets value", () => {
      const yearStart = document.getElementById("yearStart");
      const yearEnd = document.getElementById("yearEnd");
      const yearStartSlider = document.getElementById("yearStartSlider");
      // Setze einen zu hohen Wert, der auch größer als yearEnd ist
      yearStart.value = "3000";
      yearEnd.value = "2020";
      yearStart.dispatchEvent(new Event("blur"));
      // Zwei Alerts sollen ausgelöst werden: Einer für "cannot be more than 2024", einer für "cannot be greater than the end year"
      expect(global.alert).toHaveBeenNthCalledWith(1, "Start year cannot be more than 2024.");
      expect(global.alert).toHaveBeenNthCalledWith(2, "The start year cannot be greater than the end year.");
      // Laut Code wird dann der Wert auf 1763 gesetzt
      expect(yearStart.value).toBe("1763");
      expect(yearStartSlider.value).toBe("1763");
    });

    test("Blur on yearEnd with valid input does not trigger alert", () => {
      const yearEnd = document.getElementById("yearEnd");
      const yearEndSlider = document.getElementById("yearEndSlider");
      const yearStart = document.getElementById("yearStart");
      // Setze einen gültigen Wert, der innerhalb des Bereichs liegt und größer als yearStart
      yearEnd.value = "2010";
      yearStart.value = "2000";
      yearEnd.dispatchEvent(new Event("blur"));
      expect(global.alert).not.toHaveBeenCalled();
      expect(yearEndSlider.value).toBe("2010");
    });

    test("Blur on yearEnd outside range triggers alert and resets value", () => {
      const yearEnd = document.getElementById("yearEnd");
      const yearEndSlider = document.getElementById("yearEndSlider");
      yearEnd.value = "1500";
      yearEnd.dispatchEvent(new Event("blur"));
      expect(global.alert).toHaveBeenCalledWith("End year cannot be less than 1763.");
      expect(yearEnd.value).toBe("1763");
      expect(yearEndSlider.value).toBe("1763");
    });
  });

  // ----------------------------------
  // Radius Logic
  // ----------------------------------
  describe("Radius Logic", () => {
    test("RadiusSlider input synchronizes radius value", () => {
      const radius = document.getElementById("radius");
      const radiusSlider = document.getElementById("radiusSlider");
      radiusSlider.value = "60";
      radiusSlider.dispatchEvent(new Event("input"));
      expect(radius.value).toBe("60");
    });

    test("Blur on radius with valid input does not trigger alert", () => {
      const radius = document.getElementById("radius");
      const radiusSlider = document.getElementById("radiusSlider");
      radius.value = "75";
      radius.dispatchEvent(new Event("blur"));
      expect(global.alert).not.toHaveBeenCalled();
      expect(radiusSlider.value).toBe("75");
    });

    test("Blur on radius with invalid input triggers alert and resets value", () => {
      const radius = document.getElementById("radius");
      const radiusSlider = document.getElementById("radiusSlider");
      radius.value = "abc";
      radius.dispatchEvent(new Event("blur"));
      expect(global.alert).toHaveBeenCalledWith("Please enter a valid integer for radius.");
      expect(radius.value).toBe("50");
      expect(radiusSlider.value).toBe("50");
    });
  });

  // ----------------------------------
  // Stations Input & Box Logic
  // ----------------------------------
  describe("Stations Input & Box Logic", () => {
    test("Blur on stationsInput with non-positive value triggers alert and resets value", () => {
      const stationsInput = document.getElementById("stationsInput");
      stationsInput.value = "-1";
      stationsInput.dispatchEvent(new Event("blur"));
      expect(global.alert).toHaveBeenCalledWith("The number of stations must be a positive integer.");
      expect(stationsInput.value).toBe("");
    });

    test("Clicking on a station-box sets .selected and updates stationsInput", () => {
      const stationBoxes = document.querySelectorAll(".station-box");
      const stationsInput = document.getElementById("stationsInput");
      // Setze Datenattribute
      stationBoxes[0].dataset.value = "5";
      stationBoxes[1].dataset.value = "10";
      stationBoxes[1].click();
      expect(stationBoxes[0].classList.contains("selected")).toBe(false);
      expect(stationBoxes[1].classList.contains("selected")).toBe(true);
      expect(stationsInput.value).toBe("10");
    });

    test("Typing in stationsInput removes .selected from all station-boxes", () => {
      const stationBoxes = document.querySelectorAll(".station-box");
      const stationsInput = document.getElementById("stationsInput");
      stationBoxes.forEach(box => box.classList.add("selected"));
      stationsInput.value = "123";
      stationsInput.dispatchEvent(new Event("input"));
      stationBoxes.forEach(box => {
        expect(box.classList.contains("selected")).toBe(false);
      });
    });
  });

  // ----------------------------------
  // List, Table & Chart Logic
  // ----------------------------------
  describe("List, Table & Chart Logic", () => {
    beforeEach(() => {
      // Erzeuge Container und Canvas
      document.body.innerHTML += `
        <ul id="stationsList"></ul>
        <table id="station-data-table-testTable">
          <tr><td>Year</td><td></td><td></td></tr>
          <tr><td>2000</td><td></td><td></td></tr>
          <tr><td>2001</td><td></td><td></td></tr>
        </table>
        <canvas id="station-data-chart-test"></canvas>
      `;
      // Mock Chart-Konstruktor
      global.Chart = jest.fn();
    });

    test("createList() populates stationsList if stations array is not empty", () => {
      const stations = [
        [["id1", "Station1", 10, 20], 123]
      ];
      createList(stations, "2000", "2020", ["Year", "Header1", "Header2"]);
      const list = document.getElementById("stationsList");
      expect(list.children.length).toBe(1);
    });

    test("createList() logs message if stations array is empty", () => {
      createList([], "2000", "2020", ["Year", "Header1", "Header2"]);
      expect(global.console.log).toHaveBeenCalledWith("Keine Einträge vorhanden.");
    });

    test("fillTable() populates table cells with formatted values", () => {
      const data = [
        [[2000, 10], [2001, 20]]
      ];
      fillTable(data, "testTable");
      const table = document.getElementById("station-data-table-testTable");
      expect(table.rows[1].cells[1].textContent).toBe("10.0");
      expect(table.rows[2].cells[1].textContent).toBe("20.0");
    });

    test("fillTable() does nothing if table not found", () => {
      expect(() => fillTable([], "nonexistent")).not.toThrow();
    });

    test("createChart() creates a Chart of type 'line' for positive latitude", () => {
      const data = [
        [[2000, 10], [2001, 20]],
        [[2000, 15], [2001, 25]]
      ];
      const titleSeason = ["Year", "Header1", "Header2"];
      createChart(data, titleSeason, "test", 10);
      expect(global.Chart).toHaveBeenCalled();
      const chartConfig = global.Chart.mock.calls[0][1];
      expect(chartConfig.type).toBe("line");
    });

    test("createChart() uses alternative colors for negative latitude", () => {
      const data = [
        [[2000, 10], [2001, 20]]
      ];
      const titleSeason = ["Year", "Header1", "Header2"];
      createChart(data, titleSeason, "test", -10);
      expect(global.Chart).toHaveBeenCalled();
      const chartConfig = global.Chart.mock.calls[0][1];
      // Hier prüfen wir, dass der BorderColor-Wert gesetzt ist (ein rgb()-String)
      expect(chartConfig.data.datasets[0].borderColor).toMatch(/rgb\(/);
    });

    test("toggleContent() toggles classes on content and arrow", () => {
      toggleContent("test");
      let content = document.getElementById("station-data-div-test");
      let arrow = document.getElementById("arrow-test");
      expect(content.classList.contains("open")).toBe(true);
      expect(arrow.classList.contains("rotated")).toBe(true);
      toggleContent("test");
      expect(content.classList.contains("open")).toBe(false);
      expect(arrow.classList.contains("rotated")).toBe(false);
    });

    test("scrollToStation() calls scrollIntoView on content", () => {
      scrollToStation("test");
      const content = document.getElementById("station-data-div-test");
      // Da toggleContent und getStationData wurden im Test gestubbt (z. B. global.toggleContent = jest.fn())
      // prüfen wir, ob scrollIntoView aufgerufen wurde.
      expect(Element.prototype.scrollIntoView).toHaveBeenCalled();
    });

    test("scrollToStation() does nothing if content element is not found", () => {
      document.body.innerHTML = "";
      expect(() => scrollToStation("nonexistent")).not.toThrow();
    });
  });
});


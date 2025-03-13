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
    const logo = document.getElementById("logo");
    logo.src = logo.getAttribute("data-light");

    global.alert = jest.fn();
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  describe("validateInput()", () => {
    test("should set input value to min if value is below minimum", () => {
      const input = { value: "100" }; // als Zahl wird hier 100 interpretiert
      validateInput(input, 1763, 2024, "Test");
      expect(input.value).toBe(1763);
    });
    test("should set input value to max if value is above maximum", () => {
      const input = { value: "2500" };
      validateInput(input, 1763, 2024, "Test");
      expect(input.value).toBe(2024);
    });
    test("should leave input unchanged if within range", () => {
      const input = { value: "2000" };
      validateInput(input, 1763, 2024, "Test");
      expect(input.value).toBe("2000");
    });
  });

  describe("List & Table Functions", () => {
    test("clearList() should empty the stationsList container", () => {
      const list = document.getElementById("stationsList");
      list.innerHTML = "<li>Item</li>";
      clearList();
      expect(list.innerHTML).toBe("");
    });

    test("createList() should populate stationsList if stations array is not empty", () => {
      const stations = [
        [["id1", "Station1", 10, 20], 123],
        [["id2", "Station2", 30, 40], 456]
      ];
      createList(stations, "2000", "2020", ["Year", "Header1", "Header2"]);
      const list = document.getElementById("stationsList");
      expect(list.children.length).toBe(2);
    });

    test("fillTable() populates table cells with formatted values", () => {
      document.body.innerHTML = `
        <table id="station-data-table-testTable">
          <tr><td>Year</td><td></td><td></td></tr>
          <tr><td>2000</td><td></td><td></td></tr>
          <tr><td>2001</td><td></td><td></td></tr>
        </table>
      `;
      const data = [
        [[2000, 10], [2001, 20]]
      ];
      fillTable(data, "testTable");
      const table = document.getElementById("station-data-table-testTable");
      expect(table.rows[1].cells[1].textContent).toBe("10.0");
      expect(table.rows[2].cells[1].textContent).toBe("20.0");
    });
  });

  describe("addStation()", () => {
  test("should add a new station to the stations list", () => {
    const list = document.getElementById("stationsList");
    const station = [["id1", "Test Station", 10, 20], 123]; // Richtige Struktur
    const titleSeason = ["Year", "Header1", "Header2"];
    addStation(station, 2000, 2020, titleSeason);
    expect(list.children.length).toBe(1);
    expect(list.children[0].textContent).toContain("Test Station");
    expect(list.children[0].textContent).toContain("123.0 km"); // Erwartung anpassen auf Dezimalformat
  });

  test("should handle multiple calls and add multiple stations", () => {
    const list = document.getElementById("stationsList");
    const stationA = [["id3", "Station A", 12, 22], 150.2];
    const stationB = [["id4", "Station B", 18, 28], 75.3];
    const titleSeason = ["Year", "Header1", "Header2"];
    addStation(stationA, 2000, 2020, titleSeason);
    addStation(stationB, 2000, 2020, titleSeason);
    expect(list.children.length).toBe(2);
    expect(list.children[0].textContent).toContain("Station A");
    expect(list.children[0].textContent).toContain("150.2 km");
    expect(list.children[1].textContent).toContain("Station B");
    expect(list.children[1].textContent).toContain("75.3 km");
  });
});

  describe("toggleContent()", () => {
    test("should toggle 'open' on content and 'rotated' on arrow", () => {
      // Die Elemente haben in diesem Fall die IDs, die toggleContent erwartet:
      document.body.innerHTML = `
        <div id="station-data-div-test"></div>
        <img id="arrow-test" class="toggle-arrow" />
      `;
      toggleContent("test");
      let content = document.getElementById("station-data-div-test");
      let arrow = document.getElementById("arrow-test");
      expect(content.classList.contains("open")).toBe(true);
      expect(arrow.classList.contains("rotated")).toBe(true);
      toggleContent("test");
      expect(content.classList.contains("open")).toBe(false);
      expect(arrow.classList.contains("rotated")).toBe(false);
    });
  });

  describe("createChart()", () => {
    beforeEach(() => {
      document.body.innerHTML = `<canvas id="station-data-chart-test"></canvas>`;
      global.Chart = jest.fn();
    });
    test("should create a Chart with type 'line'", () => {
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
  });

  describe("scrollToStation()", () => {
    beforeEach(() => {
      document.body.innerHTML = `
        <div id="station-data-div-test"></div>
        <img id="arrow-test" class="toggle-arrow" />
      `;
      Element.prototype.scrollIntoView = jest.fn();
      global.toggleContent = jest.fn();
      global.getStationData = jest.fn();
    });
    test("should call scrollIntoView on the content element", () => {
      scrollToStation("test");
      const content = document.getElementById("station-data-div-test");
      expect(Element.prototype.scrollIntoView).toHaveBeenCalled();
    });
  });
})




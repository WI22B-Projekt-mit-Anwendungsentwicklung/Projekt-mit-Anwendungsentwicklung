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
 * =========================================================
 */

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
    jest.resetModules();
    require("../../src/static/js/routes.js");

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
      await global.getStations();
      expect(global.fetch).not.toHaveBeenCalled();
    });

    test("Should fetch with correct body, show alert if result is empty", async () => {
      document.getElementById("latitude").value = "45";
      document.getElementById("longitude").value = "9";
      global.fetch.mockResolvedValue({
        json: async () => []
      });

      await global.getStations();
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

      await global.getStations();
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

      await global.getStations();
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
      await global.getStations();
      expect(global.console.error).toHaveBeenCalledWith(
        "Fehler beim Senden der Daten:",
        expect.any(Error)
      );
    });
  });

  // getStationData TESTS
  describe("getStationData()", () => {
    test("Should call fillTable + createChart on success", async () => {
      document.getElementById("latitude").value = "0";

      // Test-Data
      const mockResult = [["2000", 10], ["2001", 12]];
      global.fetch.mockResolvedValue({
        json: async () => mockResult
      });

      await global.getStationData("idX");
      expect(global.fetch).toHaveBeenCalledWith("http://localhost:8000/get_weather_data", expect.any(Object));
      expect(global.fillTable).toHaveBeenCalledWith(mockResult, "idX");
      expect(global.createChart).toHaveBeenCalledWith(mockResult, expect.any(Array), "idX", "0");
    });

    test("Should use alternative seasons if latitude < 0", async () => {
      document.getElementById("latitude").value = "-12"; // lat < 0
      global.fetch.mockResolvedValue({ json: async () => [] });
      await global.getStationData("idY");
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
      await global.getStationData("idZ");
      expect(global.console.error).toHaveBeenCalledWith(
        "Fehler beim Senden der Daten:",
        expect.any(Error)
      );
    });
  });
});
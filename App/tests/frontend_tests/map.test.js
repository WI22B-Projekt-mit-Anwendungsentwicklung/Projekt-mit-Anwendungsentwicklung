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

describe("Tests for map.js", () => {
  let originalAlert;
  let mockLatLng;

  beforeAll(() => {
    // Setze globale Mocks, bevor das Modul importiert wird
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
    originalAlert = window.alert;
    window.alert = jest.fn();
    global.alert = window.alert;
  });

  beforeEach(() => {
    jest.resetModules(); // Stellt sicher, dass das Modul frisch geladen wird

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

    document.body.innerHTML = `
      <input id="latitude" value="0" />
      <input id="longitude" value="0" />
      <input id="radius" value="50" />
      <div id="map"></div>
    `;

    global.clearList = jest.fn();
    global.getStations = jest.fn();

    require("../../src/static/js/map.js");
    global.initMap();

    mockLatLng = {
      lat: jest.fn(() => 48.858844),
      lng: jest.fn(() => 2.294351)
    };
  });

  afterEach(() => {
    window.alert = originalAlert;
    jest.clearAllMocks();
  });

  describe("handleRightClick()", () => {
    test("should update latitude and longitude inputs", () => {
      global.handleRightClick(mockLatLng);
      expect(document.getElementById("latitude").value).toBe("48.858844");
      expect(document.getElementById("longitude").value).toBe("2.294351");
    });
  });

  describe("createCustomMarker()", () => {
    test("should return a div element with class 'custom-marker'", () => {
      const marker = global.createCustomMarker();
      expect(marker).toBeInstanceOf(HTMLDivElement);
      expect(marker.classList.contains("custom-marker")).toBe(true);
    });

    test("should create an SVG with the default red color", () => {
      const marker = global.createCustomMarker();
      expect(marker.innerHTML).toContain('<path fill="#D32F2F"');
    });
  });

  describe("clearWeatherStations()", () => {
    test("should run without errors", () => {
      expect(() => {
        global.clearWeatherStations();
      }).not.toThrow();
    });
  });

  describe("addMarker()", () => {
    test("should alert if lat/long are invalid", () => {
      window.alert = jest.fn();
      document.getElementById("latitude").value = "abc";
      document.getElementById("longitude").value = "def";
      global.addMarker();
      expect(window.alert).toHaveBeenCalledWith("Please enter valid Latitude and Longitude values.");
    });

    test("should create currentMarker/currentCircle with valid lat/long", () => {
      document.getElementById("latitude").value = "10";
      document.getElementById("longitude").value = "20";
      document.getElementById("radius").value = "5";
      global.google.maps.marker.AdvancedMarkerElement.mockClear();
      global.google.maps.Circle.mockClear();
      global.addMarker();
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
      global.addRightClickListener();
      const mockMapInstance = global.google.maps.Map.mock.results[0].value;
      expect(mockMapInstance.addListener).toHaveBeenCalledWith(
        "rightclick",
        expect.any(Function)
      );
    });
  });

  describe("addWeatherStations()", () => {
    test("warns if stations.length === 0", () => {
      global.addWeatherStations([]);
      expect(global.console.warn).toHaveBeenCalledWith("No stations available to display.");
    });

    test("creates new markers for each station", () => {
      const stations = [
        [[1, "StationOne", 10, 20], 123],
        [[2, "StationTwo", 30, 40], 456],
      ];
      global.addWeatherStations(stations);
      expect(global.google.maps.marker.AdvancedMarkerElement).toHaveBeenCalledTimes(2);
      const mockMarker = global.google.maps.marker.AdvancedMarkerElement.mock.results[0].value;
      expect(mockMarker.addListener).toHaveBeenCalledWith("gmp-click", expect.any(Function));
    });
  });
});
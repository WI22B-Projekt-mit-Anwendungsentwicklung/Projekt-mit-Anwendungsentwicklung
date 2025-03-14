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
 * -> script.js
 * =========================================================
 */

// DOM-Grundstruktur für die Tests
const baseDOM = `
  <header></header>
  <input type="checkbox" id="modeToggle" />
  <img id="logo" data-light="light-logo.png" data-dark="dark-logo.png" />
  <input id="yearStart" value="2000" />
  <input id="yearEnd" value="2020" />
  <input id="yearStartSlider" type="range" min="1763" max="3000" value="2000" />
  <input id="yearEndSlider" type="range" min="1763" max="3000" value="2020" />
  <input id="radius" value="50" />
  <input id="radiusSlider" type="range" min="1" max="100" value="50" />
  <div class="station-box" data-value="5"></div>
  <div class="station-box" data-value="10"></div>
  <input id="stationsInput" />
  <ul id="stationsList"></ul>
  <canvas id="station-data-chart-test"></canvas>
  <div id="station-data-div-test"></div>
  <img id="arrow-test" class="toggle-arrow" />
`;

// Funktion zum Zurücksetzen des DOMs
function resetDOM() {
  document.body.innerHTML = baseDOM;
  const logo = document.getElementById("logo");
  if (logo) {
    logo.src = logo.getAttribute("data-light");
  }
}

beforeAll(() => {
  resetDOM();
});

beforeEach(() => {
  jest.resetModules(); // Stellt sicher, dass das Modul frisch geladen wird
  resetDOM();

  // Module laden (führt `script.js` aus)
  require("../../src/static/js/script.js");

  global.alert = jest.fn();
});

afterEach(() => {
  jest.clearAllMocks();
});

describe("Tests for script.js logic functions", () => {
  describe("validateInput()", () => {
    test("should set input value to min if value is below minimum", () => {
      const input = { value: "100" };
      global.validateInput(input, 1763, 2024, "Test");
      expect(input.value).toBe(1763);
    });

    test("should set input value to max if value is above maximum", () => {
      const input = { value: "2500" };
      global.validateInput(input, 1763, 2024, "Test");
      expect(input.value).toBe(2024);
    });

    test("should leave input unchanged if within range", () => {
      const input = { value: "2000" };
      global.validateInput(input, 1763, 2024, "Test");
      expect(input.value).toBe("2000");
    });
  });

  describe("List & Table Functions", () => {
    test("clearList() should empty the stationsList container", () => {
      const list = document.getElementById("stationsList");
      list.innerHTML = "<li>Item</li>";
      global.clearList();
      expect(list.innerHTML).toBe("");
    });

    test("createList() should populate stationsList if stations array is not empty", () => {
      const stations = [
        [["id1", "Station1", 10, 20], 123],
        [["id2", "Station2", 30, 40], 456]
      ];
      global.createList(stations, "2000", "2020", ["Year", "Header1", "Header2"]);
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
      global.fillTable(data, "testTable");
      const table = document.getElementById("station-data-table-testTable");
      expect(table.rows[1].cells[1].textContent).toBe("10.0");
      expect(table.rows[2].cells[1].textContent).toBe("20.0");
    });
  });

  describe("addStation()", () => {
    test("should add a new station to the stations list", () => {
      const list = document.getElementById("stationsList");
      const station = [["id1", "Test Station", 10, 20], 123];
      const titleSeason = ["Year", "Header1", "Header2"];
      global.addStation(station, 2000, 2020, titleSeason);
      expect(list.children.length).toBe(1);
      expect(list.children[0].textContent).toContain("Test Station");
      expect(list.children[0].textContent).toContain("123.0 km");
    });
  });

  describe("toggleContent()", () => {
    test("should toggle 'open' on content and 'rotated' on arrow", () => {
      document.body.innerHTML = `
        <div id="station-data-div-test"></div>
        <img id="arrow-test" class="toggle-arrow" />
      `;
      global.toggleContent("test");
      let content = document.getElementById("station-data-div-test");
      let arrow = document.getElementById("arrow-test");
      expect(content.classList.contains("open")).toBe(true);
      expect(arrow.classList.contains("rotated")).toBe(true);
      global.toggleContent("test");
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
      global.createChart(data, titleSeason, "test", 10);
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
      global.scrollToStation("test");
      const content = document.getElementById("station-data-div-test");
      expect(Element.prototype.scrollIntoView).toHaveBeenCalled();
    });
  });
});
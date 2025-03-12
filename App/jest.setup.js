// jest.setup.js
document.body.innerHTML = `
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
`;

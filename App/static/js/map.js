let map;
    let currentMarker = null;   // letzter Marker
    let currentCircle = null;   // aktueller Kreis

    function initMap() {
      map = new google.maps.Map(document.getElementById("map"), {
        zoom: 2,
        center: { lat: 0, lng: 0 },
        mapTypeId: google.maps.MapTypeId.TERRAIN,
        disableDefaultUI: true
      });
    }

    const radiusInput = document.getElementById('radiusInput');
    const radiusRange = document.getElementById('radius');
    const radiusValue = document.getElementById('radiusValue');
    const yearStartInput = document.getElementById('yearStart');
    const yearEndInput = document.getElementById('yearEnd');
    const yearRangeDuration = document.getElementById('yearRangeDuration');

    function updateRadiusFromRange() {
      const value = radiusRange.value;
      radiusInput.value = value;
      radiusValue.textContent = `${value} km`;
    }

    function updateRadiusFromInput() {
      const value = radiusInput.value;
      radiusRange.value = value;
      radiusValue.textContent = `${value} km`;
    }

    radiusRange.addEventListener('input', updateRadiusFromRange);
    radiusInput.addEventListener('input', updateRadiusFromInput);

    function updateYearRangeDuration() {
      const yearStart = parseInt(yearStartInput.value);
      const yearEnd = parseInt(yearEndInput.value);

      if (!isNaN(yearStart) && !isNaN(yearEnd) && yearEnd >= yearStart) {
        const duration = yearEnd - yearStart;
        yearRangeDuration.textContent = `Zeitraum: ${duration} Jahre`;
      } else {
        yearRangeDuration.textContent = "Zeitraum: - Jahre";
      }
    }

    yearStartInput.addEventListener('input', updateYearRangeDuration);
    yearEndInput.addEventListener('input', updateYearRangeDuration);

    // Marker hinzufügen / aktualisieren
    function addMarker() {
      // Entferne alten Marker und alten Kreis (falls vorhanden)
      if (currentMarker) {
        currentMarker.setMap(null);
      }
      if (currentCircle) {
        currentCircle.setMap(null);
      }

      const latitude = parseFloat(document.getElementById("latitude").value);
      const longitude = parseFloat(document.getElementById("longitude").value);

      if (isNaN(latitude) || isNaN(longitude)) {
        alert("Please enter valid Latitude and Longitude values.");
        return;
      }

      // Wert des Sliders (in km) in Meter umrechnen
      const radiusKm = parseFloat(radiusRange.value);
      const radiusInMeters = radiusKm * 1000;

      const position = { lat: latitude, lng: longitude };

      // Neuen Marker setzen
      currentMarker = new google.maps.Marker({
        position: position,
        map: map,
        title: "Weather Station"
      });

      // Karte zentrieren und heranzoomen
      map.setCenter(position);
      map.setZoom(10);

      // Kreis zeichnen
      currentCircle = new google.maps.Circle({
        strokeColor: "#FF0000",
        strokeOpacity: 0.8,
        strokeWeight: 2,
        fillColor: "#FF0000",
        fillOpacity: 0.35,
        map: map,
        center: position,
        radius: radiusInMeters
      });

      // Zeitraum auslesen
      const yearStart = parseInt(document.getElementById("yearStart").value);
      const yearEnd = parseInt(document.getElementById("yearEnd").value);

      if (!yearStart || !yearEnd || yearStart > yearEnd) {
        alert("Please enter a valid year range.");
        return;
      }

      console.log(`Fetching weather data for years ${yearStart} to ${yearEnd}...`);
    }
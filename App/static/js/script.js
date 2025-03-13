document.getElementById('modeToggle').addEventListener("change", (event) => {
    document.body.classList.toggle("dark-mode", event.target.checked);
    const logo = document.getElementById("logo");
    logo.src = event.target.checked ? logo.getAttribute("data-dark") : logo.getAttribute("data-light");
});

document.addEventListener('scroll', () => {
    const header = document.querySelector('header');
    header.classList.toggle('scrolled', window.scrollY > 0);
});

document.getElementById('yearStartSlider').addEventListener('input', (event) => {
    const yearEndSlider = document.getElementById('yearEndSlider');
    if (parseInt(event.target.value) > parseInt(yearEndSlider.value)) {
        event.target.value = yearEndSlider.value;
    }
    document.getElementById('yearStart').value = event.target.value;
});

document.getElementById('yearEndSlider').addEventListener('input', (event) => {
    const yearStartSlider = document.getElementById('yearStartSlider');
    if (parseInt(event.target.value) < parseInt(yearStartSlider.value)) {
        event.target.value = yearStartSlider.value;
    }
    document.getElementById('yearEnd').value = event.target.value;
});

document.getElementById('yearStart').addEventListener('blur', (event) => {
    validateInput(event.target, 1763, 2024, "Start year");
    if (isNaN(parseInt(event.target.value)) || !/^-?\d{4}$/.test(event.target.value)) {
        alert("Start year must be a four-digit integer.");
        event.target.value = 1763;
    } else if (parseInt(event.target.value) > parseInt(document.getElementById('yearEnd').value)) {
        alert("The start year cannot be greater than the end year.");
        event.target.value = 1763;
    }
    document.getElementById('yearStartSlider').value = event.target.value;
});

document.getElementById('yearEnd').addEventListener('blur', (event) => {
    validateInput(event.target, 1763, 2024, "End year");
    if (isNaN(parseInt(event.target.value)) || !/^-?\d{4}$/.test(event.target.value)) {
        alert("End year must be a four-digit integer.");
        event.target.value = 2024;
    } else if (parseInt(event.target.value) < parseInt(document.getElementById('yearStart').value)) {
        alert("The end year cannot be greater than the start year.");
        event.target.value = 2024;
    }
    document.getElementById('yearEndSlider').value = event.target.value;
});

document.getElementById('radiusSlider').addEventListener('input', (event) => {
    document.getElementById('radius').value = event.target.value;
});

document.getElementById('radius').addEventListener('blur', (event) => {
    validateInput(event.target, 1, 100, "Radius");
    if (isNaN(parseInt(event.target.value)) || !/^\d+$/.test(event.target.value)) {
        alert("Please enter a valid integer for radius.");
        event.target.value = 50;
    }
    document.getElementById('radiusSlider').value = event.target.value;
});

document.getElementById('stationsInput').addEventListener("blur", (event) => {
    let value = event.target.value.trim();
    if (!/^\d+$/.test(value) || parseInt(value) <= 0) {
        alert("The number of stations must be a positive integer.");
        event.target.value = null;
    }
});

document.querySelectorAll('.station-box').forEach(box => {
    box.addEventListener('click', function () {
        document.querySelectorAll('.station-box').forEach(b => b.classList.remove('selected'));
        this.classList.add('selected');
        document.getElementById('stationsInput').value = this.dataset.value;
    });
});

document.getElementById('stationsInput').addEventListener('input', () => {
    document.querySelectorAll('.station-box').forEach(b => b.classList.remove('selected'));
});

export function validateInput(input, min, max, message) {
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

document.addEventListener('DOMContentLoaded', function() {
    const temperatureSlider = document.getElementById('temperature');
    const temperatureValue = document.getElementById('temperatureValue');

    temperatureSlider.addEventListener('input', function() {
        temperatureValue.textContent = this.value;
        updateSliderBackground(this);
    });

    // Initialize Tippy.js tooltips
    tippy('[data-tippy-content]', {
        placement: 'right',
        arrow: true,
        theme: 'light-border'
    });

    // Initialize slider background
    updateSliderBackground(temperatureSlider);
});

function updateSliderBackground(slider) {
    const value = (slider.value - slider.min) / (slider.max - slider.min) * 100;
    slider.style.background = `linear-gradient(to right, #191970 0%, #191970 ${value}%, #e9ecef ${value}%, #e9ecef 100%)`;
}
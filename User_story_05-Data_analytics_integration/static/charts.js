document.addEventListener("DOMContentLoaded", function () {
    fetch("/data")
        .then(response => response.json())
        .then(data => {
            createChart("donationChart", "Donations", data.donations);
            createChart("volunteerChart", "Volunteers", data.volunteers);
            createChart("registrationChart", "Registrations", data.registrations);
        });

    function createChart(canvasId, label, data) {
        new Chart(document.getElementById(canvasId), {
            type: 'line',
            data: {
                labels: ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
                datasets: [{
                    label: label,
                    data: data,
                    borderColor: "blue",
                    fill: false
                }]
            }
        });
    }
});

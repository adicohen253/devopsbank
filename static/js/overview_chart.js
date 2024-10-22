// Extract labels (dates) and values (totals) from overview data
var labels = overview.map(item => item.date);
var values = overview.map(item => item.total);

// Sort data by date (assuming date format is "DD/MM/YYYY")
var sortedData = overview.sort((a, b) => {
    return new Date(a.date.split('/').reverse().join('/')) - new Date(b.date.split('/').reverse().join('/'));
});

// Update labels and values arrays with sorted data
labels = sortedData.map(item => item.date);
values = sortedData.map(item => item.total);

// Find the maximum absolute value to set symmetric axis
var maxAbs = Math.max(...values.map(Math.abs));

// Function to round up to the nearest multiple of 50
function roundUpToNearestMultiple(value, multiple) {
    return Math.ceil(value / multiple) * multiple;
}

// Calculate the max value for the y-axis rounded up to the nearest 50
var maxYAxisValue = roundUpToNearestMultiple(maxAbs, 100);

// Chart.js configuration
var ctx = document.getElementById('myChart').getContext('2d');
var myChart = new Chart(ctx, {
    type: 'bar',
    data: {
        labels: labels,
        datasets: [{
            label: 'Total daily',
            data: values,
            backgroundColor: values.map(value => value >= 0 ? 'green' : 'red'),
            barThickness: 10  // Adjust this value to make the bars thinner or thicker
        }]
    },
    options: {
        plugins: {
            legend: {
                display: false
            }
        },
        scales: {
            x: {
                grid: {
                    display: false
                },
                title: {
                    display: true,
                    text: 'Dates'  // X-axis title
                }
            },
            y: {
                min: -maxYAxisValue,  // Ensure the minimum y-axis value is negative of the rounded max value
                max: maxYAxisValue,   // Ensure the maximum y-axis value is the rounded max value
                ticks: {
                    stepSize: 50 // Set the step size for the y-axis ticks
                },
                grid: {
                    display: true
                },
                title: {
                    display: true,
                    text: 'Total Amount in $'  // Y-axis title
                }
            }
        }
    }
});

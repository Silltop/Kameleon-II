// Provided formatBytes function
function formatBytes(bytes, decimals = 2) {
    if (bytes === 0) return '0 Bytes';

    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];

    const i = Math.floor(Math.log(bytes) / Math.log(k));

    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
}

// Function to create a disk usage chart
function createDiskChart(canvasId, inputData) {
    // Convert disk space values to decimals using formatBytes function
    inputData.forEach(entry => {
        entry.size = formatBytes(parseInt(entry.size));
        entry.used = formatBytes(parseInt(entry.used));
    });

    // Extracting data for labels and datasets
    const labels = inputData.map(entry => entry.mountpoint); // Extract mountpoints for labels
    const usedSpaceData = inputData.map(entry => parseFloat(entry.used)); // Extract used space data
    const availableSpaceData = inputData.map(entry => parseFloat(entry.size) - parseFloat(entry.used)); // Calculate available space data


    // Creating the Chart.js compatible data object
    const data = {
        labels: labels,
        datasets: [{
            label: 'Used Space',
            data: usedSpaceData,
            backgroundColor: 'rgba(255, 99, 132, 0.6)', // Red for used space
            borderColor: 'rgba(255, 99, 132, 1)',
            borderWidth: 1
        }, {
            label: 'Available Space',
            data: availableSpaceData,
            backgroundColor: 'rgba(54, 162, 235, 0.6)', // Blue for available space
            borderColor: 'rgba(54, 162, 235, 1)',
            borderWidth: 1
        }]
    };

    // Configuration for the chart
    const config = {
        type: 'bar',
        data: data,
        options: {
            indexAxis: 'y', // Display bars horizontally
            responsive: true,
            plugins: {
                title: {
                    display: true,
                    text: 'Disk Storage Status'
                }
            },
            scales: {
                x: {
                    stacked: true,
                },
                y: {
                    stacked: true
                }
            }
        },
    };

    // Get the canvas element
    const ctx = document.getElementById(canvasId).getContext('2d');

    // Create the chart
    new Chart(ctx, config);
}
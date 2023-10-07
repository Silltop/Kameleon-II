function createDiskSpaceChart(usedSpaceBytes, totalSpaceBytes, chartId) {
  // Convert bytes to the highest appropriate unit and format as a string
  function formatBytes(bytes, decimals = 2) {
    if (bytes === 0) return '0 Bytes';

    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];

    const i = Math.floor(Math.log(bytes) / Math.log(k));

    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
  }

  const usedSpace = formatBytes(usedSpaceBytes);
  const totalSpace = formatBytes(totalSpaceBytes);
  const freeSpaceBytes = totalSpaceBytes - usedSpaceBytes;
  const freeSpace = formatBytes(freeSpaceBytes);

  // Calculate the percentage of used and free space
  const usedSpacePercentage = (usedSpaceBytes / totalSpaceBytes) * 100;
  const freeSpacePercentage = (freeSpaceBytes / totalSpaceBytes) * 100;

  new Chart(
    document.getElementById(chartId),
    {
      type: 'doughnut',
      data: {
        labels: ['Used Space', 'Free Space'],
        datasets: [{
          data: [usedSpacePercentage, freeSpacePercentage],
          backgroundColor: [
            'rgba(255, 99, 132, 0.7)', // Red for Used Space
            'rgba(0, 255, 0, 0.7)',     // Green for Free Space
          ],
        }],
      },
      options: {
        animation: false,
        responsive: false,

        plugins: {
           title: {
            display: true,
            text: 'Total Space: ' + totalSpace,
            position: 'bottom',
            },
          legend: {
            display: false,
          },
          tooltip: {
            enabled: true,
            callbacks: {
              label: function (context) {
                const dataIndex = context.dataIndex;
                if (context.dataIndex === 0) {
                  return 'Used Space: ' + usedSpace + ' (' + usedSpacePercentage.toFixed(2) + '%)';
                } else {
                  return 'Free Space: ' + freeSpace + ' (' + freeSpacePercentage.toFixed(2) + '%)';
                }
              },
            },
          },
        },
      },
    }
  );
}
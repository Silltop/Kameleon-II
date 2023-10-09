function createChart(chartElement, chartType, data, precision, title) {
  new Chart(
      document.getElementById(chartElement),
      {
        type: chartType,
        data: {
          labels: data.map(item => item.label),
          datasets: [{
            data: data.map(item => item.value),
            backgroundColor: data.map(item => item.color),
          }],
        },
        options: {
          animation: false,
          responsive: false,
          scale: {
            ticks: {
              precision: precision
            }
          },
          plugins: {
            legend: {
              display: false,
              position: 'bottom',
            },
            tooltip: {
              enabled: true,
            },
            title: {
            display: true,
            text: title
            },
          },
        },
      }
    );
}

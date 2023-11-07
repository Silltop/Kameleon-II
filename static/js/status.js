    function fetchAndUpdateStatus() {
      // Replace the URL with your JSON data source
      const apiUrl = '/uptime';

      fetch(apiUrl)
        .then((response) => response.json())
        .then((rdata) => {
          for (const ip in rdata) {
            const status = rdata[ip][0];
            const rows = document.querySelectorAll(".t-row");
            rows.forEach((row) => {
              const nameCell = row.firstElementChild;
              const iconElement = nameCell.firstElementChild;
              if (nameCell.textContent.includes(ip)) {

                if (status === 'Connection Error') {
                    iconElement.style.backgroundColor = 'red';
                    iconElement.style.boxShadow = '0 0 0 3px rgba(255, 51, 51, 0.8)';
                  }
                  else {
                    iconElement.style.backgroundColor = 'green';
                    iconElement.style.boxShadow = '0 0 0 3px rgba(51, 255, 51, 0.8)';
                  }
              }
            });
          }
        })
        .catch((error) => {
          console.error('Error:', error);
        });
    }
    // Call the function initially and then every 10 seconds
    fetchAndUpdateStatus();
    setInterval(fetchAndUpdateStatus, 10000); // 10 seconds in milliseconds

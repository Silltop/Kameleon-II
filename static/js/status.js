function fetchAndUpdateStatus() {
  const apiUrl = '/uptime';  // Replace with your API URL

  fetch(apiUrl)
    .then((response) => response.json())
    .then((rdata) => {
      const rows = document.querySelectorAll(".t-row");  // Get all rows once

      rows.forEach((row) => {
        const nameCell = row.firstElementChild;
        const iconElement = nameCell.firstElementChild;

        // Extract IP from the row content (assumes the IP is present in the text)
        const rowIP = nameCell.textContent.trim();

        if (rdata[rowIP]) {  // Check if the IP exists in the fetched data
          const uptime = rdata[rowIP].uptime;
          // Example logic: Assume connection error if `uptime` is missing or empty
          if (!uptime || uptime === 'Connection Error') {
            iconElement.style.backgroundColor = 'red';
            iconElement.style.boxShadow = '0 0 0 3px rgba(255, 51, 51, 0.8)';
          } else {
            iconElement.style.backgroundColor = 'green';
            iconElement.style.boxShadow = '0 0 0 3px rgba(51, 255, 51, 0.8)';
          }
        } else {
          // If IP is not in the response, mark it as a connection error
          iconElement.style.backgroundColor = 'red';
          iconElement.style.boxShadow = '0 0 0 3px rgba(255, 51, 51, 0.8)';
        }
      });
    })
    .catch((error) => {
      console.error('Error:', error);
    });
}

// Call the function initially and then every 10 seconds
fetchAndUpdateStatus();
setInterval(fetchAndUpdateStatus, 10000);  // 10 seconds in milliseconds

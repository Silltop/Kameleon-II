function decodeBase64(encodedMessage) {
    let decodedMessage = atob(encodedMessage);  // Decode the Base64 message
    return decodedMessage;
}

document.addEventListener('DOMContentLoaded', function () {
    var logContainer = document.getElementById('log-container');
    if (!logContainer) return; // Ensure logContainer exists

    var loadingSpinner = logContainer.querySelector('.loading-spinner');
    if (!loadingSpinner) return; // Ensure loadingSpinner exists

    // Simulate loading with a delay (replace this with your actual log-fetching logic)
    setTimeout(function () {
        // When logs are ready, hide the loading spinner
        loadingSpinner.classList.add('hidden');
        logContainer.innerHTML = "";
        // Replace the loading text with actual logs (or the real content)
    }, 2000); // Simulate 2 seconds of loading time
});

function fetchLogs(ansibleRunId) {
    var logContainer = document.getElementById('log-container');
    var loadingSpinner = logContainer.querySelector('.loading-spinner');

    loadingSpinner.classList.remove('hidden');

    const eventSource = new EventSource('/logs-stream/' + ansibleRunId);

    eventSource.onmessage = function(event) {
        const logMessage = document.createElement('p');
        let decodedLog = decodeBase64(event.data);  // Decode the log message
        console.log(decodedLog);
        logMessage.innerHTML = highlightKeywords(decodedLog);
        logContainer.appendChild(logMessage);
        logContainer.scrollTop = logContainer.scrollHeight;
    };

    // Handle errors during log fetching
    eventSource.onerror = function(event) {
        console.error('Error fetching logs:', event);
        eventSource.close();  // Close the connection on error
    };

    // Handle stream closure if the backend signals completion
    eventSource.addEventListener('close', function(event) {
        console.log('Stream closed:', event.data);
        eventSource.close();  // Gracefully close the connection
    });
}

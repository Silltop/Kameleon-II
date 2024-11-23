function decodeBase64(encodedMessage) {
    let decodedMessage = atob(encodedMessage);  // Decode the Base64 message
    return decodedMessage;
}

document.addEventListener('DOMContentLoaded', function () {
    var logContainer = document.getElementById('log-container');
    var loadingSpinner = logContainer.querySelector('.loading-spinner');

    // Simulate loading with a delay (replace this with your actual log-fetching logic)
    setTimeout(function () {
        // When logs are ready, hide the loading spinner
        loadingSpinner.classList.add('hidden');
        logContainer.innerHTML = "";
        // Replace the loading text with actual logs (or the real content)
    }, 2000); // Simulate 2 seconds of loading time
});

function fetchLogs(ansibleRunId) {
    // Create an EventSource connection for Server-Sent Events (SSE)
    var logContainer = document.getElementById('log-container');
    var loadingSpinner = logContainer.querySelector('.loading-spinner');
    loadingSpinner.classList.remove('hidden');

    const eventSource = new EventSource('/logs-stream/' + ansibleRunId);

    // Listen for new log messages from the server
    eventSource.onmessage = function(event) {
        const logContainer = document.getElementById('log-container');

        // Create a new <p> element to hold the decoded log message
        const logMessage = document.createElement('p');
        let decodedLog = decodeBase64(event.data);  // Decode the log message
        console.log(decodedLog);
        // Set the text content of the <p> element to the decoded log message
        logMessage.textContent = decodedLog;
        // Append the <p> element to the log container
        logContainer.appendChild(logMessage);
        // Scroll to the bottom of the log container for new messages
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
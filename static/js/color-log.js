function highlightKeywords(logMessage) {
    // Keywords to search for (case-insensitive)
    const keywords = {
        'fatal': 'fatal',
        'error': 'error',
        'warning': 'warning'
    };

    // Highlight the keywords using a regular expression
    return logMessage.replace(
        new RegExp(Object.keys(keywords).join("|"), "gi"),
        (match) => {
            let lowerMatch = match.toLowerCase();
            if (lowerMatch === 'fatal') {
                return `<span class="fatal">${match}</span>`;
            } else if (lowerMatch === 'error') {
                return `<span class="red">${match}</span>`;
            } else if (lowerMatch === 'warning') {
                return `<span class="orange">${match}</span>`;
            }
            else if (lowerMatch === 'failed!') {
                return `<span class="fatal">${match}</span>`;
            }
            return match;  // Default return if no match
        }
    );
}
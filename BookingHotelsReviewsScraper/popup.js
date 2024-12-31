document.getElementById('scrapeButton').addEventListener('click', function() {
    chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
        chrome.scripting.executeScript({
            target: {tabId: tabs[0].id},
            files: ['content.js']
        }, (injectionResults) => {
            for (const frameResult of injectionResults) {
                console.log('Result from content script:', frameResult.result);
            }
        });
    });
});

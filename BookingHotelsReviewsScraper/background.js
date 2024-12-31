chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {
    if (request.action === "scrape") {
        chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
            chrome.scripting.executeScript({
                target: {tabId: tabs[0].id},
                files: ['content.js']
            }, () => {
                console.log("Script injected and executed.");
            });
        });
    }
});

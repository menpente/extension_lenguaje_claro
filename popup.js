document.addEventListener('DOMContentLoaded', function() {
  // Load saved style preference
  chrome.storage.sync.get(['simplificationStyle'], function(result) {
    if (result.simplificationStyle) {
      document.getElementById('simplificationStyle').value = result.simplificationStyle;
    }
  });

  // Save style preference when changed
  document.getElementById('simplificationStyle').addEventListener('change', function(e) {
    chrome.storage.sync.set({ simplificationStyle: e.target.value });
  });

  // Simplify button click handler
  document.getElementById('simplifyButton').addEventListener('click', function() {
    const style = document.getElementById('simplificationStyle').value;
    chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
      chrome.tabs.sendMessage(tabs[0].id, {
        action: 'simplify',
        style: style
      });
    });
    window.close();
  });
});

// background.js
chrome.action.onClicked.addListener((tab) => {
  chrome.scripting.executeScript({
    target: { tabId: tab.id },
    files: ['content.js']
  });
});

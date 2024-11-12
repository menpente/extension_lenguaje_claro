chrome.action.onClicked.addListener((tab) => {
  chrome.scripting.executeScript({
    target: { tabId: tab.id },
    function: simplifyPage
  });
});

function simplifyPage() {
  // Show loading state
  const originalContent = document.body.innerHTML;
  document.body.innerHTML = `
    <div style="padding: 20px;">
      <h1>Simplifying content...</h1>
      <p>Please wait while we process the page.</p>
    </div>
  `;

  // Collect all text content from the page
  const textContent = originalContent;
  
  // Send to hosted backend
  fetch('https://your-api-domain.com/simplify', {  // Replace with your actual API domain
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ text: textContent })
  })
  .then(response => response.json())
  .then(data => {
    if (data.status === 'error') {
      throw new Error(data.error);
    }
    // Replace page content with simplified version
    document.body.innerHTML = `
      <div style="padding: 20px; max-width: 800px; margin: 0 auto;">
        <h1>Simplified Version</h1>
        <button onclick="document.body.innerHTML = originalContent" 
                style="margin-bottom: 20px; padding: 8px 16px; cursor: pointer;">
          Show Original
        </button>
        <div style="line-height: 1.6;">${data.simplified_text}</div>
      </div>
    `;
  })
  .catch(error => {
    console.error('Error:', error);
    document.body.innerHTML = `
      <div style="padding: 20px; color: red;">
        <h1>Error</h1>
        <p>${error.message}</p>
        <button onclick="document.body.innerHTML = originalContent" 
                style="margin-top: 20px; padding: 8px 16px; cursor: pointer;">
          Return to Original
        </button>
      </div>
    `;
  });
}

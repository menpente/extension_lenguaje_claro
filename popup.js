function simplifyPage(style) {
  const originalContent = document.body.innerHTML;
  
  document.body.innerHTML = `
    <div style="padding: 20px;">
      <h1>Simplifying content...</h1>
      <p>Please wait while we process the page.</p>
    </div>
  `;

  fetch('https://your-heroku-app.herokuapp.com/simplify', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ 
      text: originalContent,
      style: style
    })
  })
  .then(response => response.json())
  .then(data => {
    if (data.status === 'error') {
      throw new Error(data.error);
    }
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

// Listen for messages from popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'simplify') {
    simplifyPage(request.style);
  }
});

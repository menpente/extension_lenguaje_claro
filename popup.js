document.getElementById('rewrite').addEventListener('click', async () => {
  // Enviar mensaje al content script para reescribir el texto
  chrome.tabs.query({ active: true, currentWindow: true }, function (tabs) {
    chrome.scripting.executeScript({
      target: { tabId: tabs[0].id },
      function: rewritePageText
    });
  });
});

function rewritePageText() {
  // Ejemplo de función para reescribir el texto en la página
  const paragraphs = document.querySelectorAll('p');
  paragraphs.forEach(p => {
    p.textContent = "Texto reescrito aquí.";
  });
}

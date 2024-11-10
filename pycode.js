importScripts('https://cdn.jsdelivr.net/pyodide/v0.18.0/full/pyodide.js');

async function main() {
  let pyodide = await loadPyodide();
  await pyodide.runPythonAsync(`
    import pyodide
    # Código en Python para reescribir el texto
    def rewrite_text(text):
        # Implementa aquí la lógica para reescribir el texto
        return "Texto claro"
    `);
  
  let result = pyodide.globals.get('rewrite_text')('Texto original');
  console.log(result);
}

main();

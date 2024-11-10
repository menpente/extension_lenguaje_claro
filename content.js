document.addEventListener('DOMContentLoaded', function () {
  // Código para manipular el DOM
  // Ejemplo: Reescribir el contenido de los párrafos
  const paragraphs = document.querySelectorAll('p');
  paragraphs.forEach(p => {
    p.textContent = "Texto reescrito aquí.";
  });
});


console.log("Script cargado correctamente")


const body = document.body;
const herramienta = document.getElementById('theme-toggle');

console.log("Elemento herramienta aencontrado")

herramienta.addEventListener('click', () =>{
    console.log("Click detectado. Cambiando clase")
    body.classList.toggle('dark-mode')
});

//dos constantes. una agarra el id y la otra crea algo nulo si el objeto no existe
console.log("Script cargado correctamente")


const body = document.body;
const herramienta = document.getElementById('theme-toggle');

console.log("Elemento herramienta aencontrado")
//añadir evento al hacer click en el botón, es decir, debería poderse cambiar al modo oscuro

herramienta.addEventListener('click', () =>{
    console.log("Click detectado. Cambiando clase")
    body.classList.toggle('dark-mode')
});

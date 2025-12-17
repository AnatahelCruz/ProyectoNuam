document.getElementById('filtro')?.addEventListener('keyup', function () {
    const value = this.value.toLowerCase();
    document.querySelectorAll('#tabla-calificaciones tr').forEach(row => {
        row.style.display = row.textContent.toLowerCase().includes(value) ? '' : 'none';
    });
});


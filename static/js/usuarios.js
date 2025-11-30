
document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('searchInput');
    const tableRows = document.querySelectorAll('#usuariosTable tbody tr');

    searchInput.addEventListener('keyup', () => {
        const filter = searchInput.value.toLowerCase();
        tableRows.forEach(row => {
            row.style.display = row.textContent.toLowerCase().includes(filter) ? '' : 'none';
        });
    });
});

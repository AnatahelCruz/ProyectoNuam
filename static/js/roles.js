
const searchInput = document.getElementById("searchInput");
const table = document.getElementById("rolesTable");

searchInput.addEventListener("keyup", () => {
    const filter = searchInput.value.toLowerCase();
    const rows = table.getElementsByTagName("tr");

    for (let i = 1; i < rows.length; i++) {
        let cells = rows[i].getElementsByTagName("td");
        let nameCell = cells[1];
        if (nameCell) {
            let text = nameCell.textContent || nameCell.innerText;
            rows[i].style.display = text.toLowerCase().includes(filter) ? "" : "none";
        }
    }
});


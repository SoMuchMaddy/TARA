const loadCatsBtn = document.getElementById("loadCatsBtn");
const catList = document.getElementById("catList");
const catForm = document.getElementById("catForm");
const nameInput = document.getElementById("nameInput");
const statusInput = document.getElementById("statusInput");
const formTitle = document.getElementById("formTitle");
const submitBtn = document.getElementById("submitBtn");

let editingCatId = null;

async function loadCats() {
    const response = await fetch("http://127.0.0.1:8000/cats");
    const cats = await response.json();

    catList.innerHTML = "";

    for (const cat of cats) {
        const li = document.createElement("li");
        li.textContent = `${cat.name} — ${cat.status} `;

        const editBtn = document.createElement("button");
        editBtn.textContent = "Edit";

        editBtn.addEventListener("click", () => {
            nameInput.value = cat.name;
            statusInput.value = cat.status;
            editingCatId = cat.id;
            formTitle.textContent = "Edit Cat";
            submitBtn.textContent = "Update Cat";
        });

        const deleteBtn = document.createElement("button");
        deleteBtn.textContent = "Delete";

        deleteBtn.addEventListener("click", async () => {
            await fetch(`http://127.0.0.1:8000/cats/${cat.id}`, {
                method: "DELETE"
            });

            if (editingCatId === cat.id) {
                resetForm();
            }

            loadCats();
        });

        li.appendChild(editBtn);
        li.appendChild(deleteBtn);
        catList.appendChild(li);
    }
}

function resetForm() {
    editingCatId = null;
    nameInput.value = "";
    statusInput.value = "";
    formTitle.textContent = "Add Cat";
    submitBtn.textContent = "Add Cat";
}

loadCatsBtn.addEventListener("click", loadCats);

catForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const catData = {
        name: nameInput.value,
        status: statusInput.value
    };

    if (editingCatId === null) {
        await fetch("http://127.0.0.1:8000/cats", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(catData)
        });
    } else {
        await fetch(`http://127.0.0.1:8000/cats/${editingCatId}`, {
            method: "PUT",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(catData)
        });
    }

    resetForm();
    loadCats();
});
// Get references to important HTML elements from the page.
// These allow JavaScript to interact with the frontend UI.

const loadCatsBtn = document.getElementById("loadCatsBtn");
const catList = document.getElementById("catList");
const catForm = document.getElementById("catForm");
const nameInput = document.getElementById("nameInput");
const statusInput = document.getElementById("statusInput");
const formTitle = document.getElementById("formTitle");
const submitBtn = document.getElementById("submitBtn");


// This variable tracks whether the user is currently editing a cat.
// If null -> we are adding a new cat.
// If it contains an ID -> we are editing an existing cat.
let editingCatId = null;



// =========================
// LOAD ALL CATS FROM BACKEND
// =========================

// async means this function can use await.
// await pauses execution until something finishes.
async function loadCats() {

    // Send a GET request to the FastAPI backend.
    // fetch() is JavaScript's built-in way to make HTTP requests.
    const response = await fetch("http://127.0.0.1:8000/cats");

    // Convert the JSON response into a JavaScript object/array.
    const cats = await response.json();

    // Clear the current displayed cat list before rebuilding it.
    catList.innerHTML = "";

    // Loop through every cat returned by the backend.
    for (const cat of cats) {

        // Create a new <li> element for this cat.
        const li = document.createElement("li");

        // Set the visible text inside the list item.
        // Example:
        // "Milo — adopted"
        li.textContent = `${cat.name} — ${cat.status} `;


        // =========================
        // CREATE EDIT BUTTON
        // =========================

        // Create a new button element.
        const editBtn = document.createElement("button");

        // Set button text.
        editBtn.textContent = "Edit";


        // Add click behavior to the Edit button.
        editBtn.addEventListener("click", () => {

            // Fill the form inputs with the cat's current data.
            nameInput.value = cat.name;
            statusInput.value = cat.status;

            // Store the cat ID so we know which cat to update later.
            editingCatId = cat.id;

            // Change form title to indicate editing mode.
            formTitle.textContent = "Edit Cat";

            // Change button text.
            submitBtn.textContent = "Update Cat";
        });



        // =========================
        // CREATE DELETE BUTTON
        // =========================

        // Create another button element.
        const deleteBtn = document.createElement("button");

        // Set button text.
        deleteBtn.textContent = "Delete";


        // Add click behavior to the Delete button.
        deleteBtn.addEventListener("click", async () => {

            // Send DELETE request to backend API.
            await fetch(`http://127.0.0.1:8000/cats/${cat.id}`, {

                // HTTP DELETE method tells backend to remove this cat.
                method: "DELETE"
            });


            // If the deleted cat was currently being edited,
            // reset the form back to Add mode.
            if (editingCatId === cat.id) {
                resetForm();
            }

            // Reload the updated cat list from the backend.
            loadCats();
        });



        // Add buttons into the list item.
        li.appendChild(editBtn);
        li.appendChild(deleteBtn);

        // Add the finished list item into the page.
        catList.appendChild(li);
    }
}



// =========================
// RESET FORM BACK TO DEFAULT
// =========================

function resetForm() {

    // Clear editing mode.
    editingCatId = null;

    // Empty text inputs.
    nameInput.value = "";
    statusInput.value = "";

    // Restore original UI text.
    formTitle.textContent = "Add Cat";
    submitBtn.textContent = "Add Cat";
}



// =========================
// LOAD CATS BUTTON EVENT
// =========================

// When the "Load Cats" button is clicked,
// run the loadCats() function.
loadCatsBtn.addEventListener("click", loadCats);



// =========================
// FORM SUBMISSION EVENT
// =========================

// Listen for form submission.
catForm.addEventListener("submit", async (event) => {

    // Prevent page refresh.
    // HTML forms normally reload the page automatically.
    event.preventDefault();


    // Create a JavaScript object containing form data.
    const catData = {

        // Get values currently typed into inputs.
        name: nameInput.value,
        status: statusInput.value
    };



    // =========================
    // ADD NEW CAT
    // =========================

    // If editingCatId is null,
    // this means we are creating a new cat.
    if (editingCatId === null) {

        // Send POST request to backend.
        await fetch("http://127.0.0.1:8000/cats", {

            // POST means "create new data".
            method: "POST",

            // Tell backend we are sending JSON.
            headers: {
                "Content-Type": "application/json"
            },

            // Convert JavaScript object into JSON text.
            body: JSON.stringify(catData)
        });

    } else {

        // =========================
        // UPDATE EXISTING CAT
        // =========================

        // Send PUT request to backend.
        await fetch(`http://127.0.0.1:8000/cats/${editingCatId}`, {

            // PUT means "update existing data".
            method: "PUT",

            // Tell backend JSON is being sent.
            headers: {
                "Content-Type": "application/json"
            },

            // Convert object into JSON text.
            body: JSON.stringify(catData)
        });
    }


    // Reset form after submission.
    resetForm();

    // Reload updated cat list.
    loadCats();
});
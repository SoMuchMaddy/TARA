const loadCatsBtn = document.getElementById("loadCatsBtn");
const catList = document.getElementById("catList");

loadCatsBtn.addEventListener("click", async () => {
    try {
        const response = await fetch("http://127.0.0.1:8000/cats");
        console.log("Response status:", response.status);

        const cats = await response.json();
        console.log("Cats data:", cats);

        catList.innerHTML = "";

        for (const cat of cats) {
            const li = document.createElement("li");
            li.textContent = `${cat.name} — ${cat.status}`;
            catList.appendChild(li);
        }
    } catch (error) {
        console.error("Fetch failed:", error);
        alert("Failed to load cats. Check browser console.");
    }
});
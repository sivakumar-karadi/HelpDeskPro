
/* =================================
   HelpDeskPro - JavaScript
================================= */

// 1. Delete ticket confirmation
document.querySelectorAll(".delete-form").forEach((form) => {
    form.addEventListener("submit", function (event) {
        const confirmed = confirm(
            "Are you sure you want to delete this ticket?"
        );

        if (!confirmed) {
            event.preventDefault();
        }
    });
});


// 2. Automatically submit status update
document.querySelectorAll(".status-select").forEach((select) => {
    select.addEventListener("change", function () {
        const form = this.closest("form");

        if (form) {
            form.requestSubmit();
        }
    });
});


// 3. Search input keyboard shortcut
const searchInput = document.querySelector(
    '.search-form input[name="q"]'
);

if (searchInput) {
    document.addEventListener("keydown", function (event) {
        if (
            event.ctrlKey &&
            event.key.toLowerCase() === "k"
        ) {
            event.preventDefault();
            searchInput.focus();
        }
    });
}


// 4. Disable buttons after form submission
document.querySelectorAll("form").forEach((form) => {
    form.addEventListener("submit", function () {
        const submitButton = this.querySelector(
            'button[type="submit"]'
        );

        if (submitButton && !this.classList.contains("delete-form")) {
            submitButton.disabled = true;
            submitButton.textContent = "Please wait...";
        }
    });
});


// 5. Welcome message in browser console
console.log("HelpDeskPro JavaScript loaded successfully!");

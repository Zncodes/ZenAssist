
document.addEventListener("DOMContentLoaded", () => {
    const dateElement = document.getElementById("current-date");

    if (dateElement) {
        const today = new Date();

        dateElement.textContent = today.toLocaleDateString(
            "en-US",
            {
                weekday: "short",
                day: "numeric",
                month: "short",
                year: "numeric"
            }
        );
    }
});

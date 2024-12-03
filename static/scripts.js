document.addEventListener("DOMContentLoaded", () => {
    const flashMessages = document.querySelectorAll(".flash-messages li");
    if (flashMessages.length > 0) {
        setTimeout(() => {
            flashMessages.forEach(msg => msg.style.display = "none");
        }, 3000);
    }
});

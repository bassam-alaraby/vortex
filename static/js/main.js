function updateCartBadge(cartCount) {
    const cartIcon = document.querySelector(".cart-icon a");
    if (!cartIcon) {
        return;
    }

    const existingBadge = cartIcon.querySelector(".cart-badge");
    if (cartCount > 0) {
        if (existingBadge) {
            existingBadge.textContent = cartCount;
            return;
        }

        const newBadge = document.createElement("span");
        newBadge.className = "cart-badge";
        newBadge.textContent = cartCount;
        cartIcon.appendChild(newBadge);
        return;
    }

    if (existingBadge) {
        existingBadge.remove();
    }
}

window.VortexUI = {
    updateCartBadge
};

document.addEventListener("DOMContentLoaded", () => {
    const hamburger = document.getElementById("hamburger");
    const navLinks = document.querySelector(".nav-links");

    if (hamburger && navLinks) {
        hamburger.addEventListener("click", () => {
            navLinks.classList.toggle("open");
            const icon = hamburger.querySelector("i");
            if (!icon) {
                return;
            }

            icon.classList.toggle("ri-menu-line");
            icon.classList.toggle("ri-close-line");
        });
    }

    window.setTimeout(() => {
        const messages = document.querySelectorAll(".flash-message");

        messages.forEach((msg, index) => {
            window.setTimeout(() => {
                msg.style.transition = "0.3s";
                msg.style.opacity = "0";
                msg.style.transform = "translateX(0) translateY(-10px)";
                window.setTimeout(() => msg.remove(), 300);
            }, index * 200);
        });
    }, 3000);
});

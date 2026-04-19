document.addEventListener("DOMContentLoaded", () => {
    const hamburger = document.getElementById("admin-hamburger");
    const nav = document.getElementById("admin-nav");

    if (!hamburger || !nav) {
        return;
    }

    const icon = hamburger.querySelector("i");

    const setOpenState = (isOpen) => {
        nav.classList.toggle("open", isOpen);
        hamburger.setAttribute("aria-expanded", String(isOpen));

        if (icon) {
            icon.classList.toggle("ri-menu-line", !isOpen);
            icon.classList.toggle("ri-close-line", isOpen);
        }
    };

    hamburger.addEventListener("click", () => {
        const willOpen = !nav.classList.contains("open");
        setOpenState(willOpen);
    });

    nav.querySelectorAll("a").forEach((link) => {
        link.addEventListener("click", () => setOpenState(false));
    });

    document.addEventListener("keydown", (event) => {
        if (event.key === "Escape") {
            setOpenState(false);
        }
    });
});

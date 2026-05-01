const setupImagePreview = (input, container) => {
    const clearPreview = () => {
        container.innerHTML = "";
    };

    const createPreviewCard = (file, index) => {
        const card = document.createElement("label");
        card.className = "image-card";

        const radio = document.createElement("input");
        radio.type = "radio";
        radio.name = "primary_upload";
        radio.value = String(index + 1);

        const img = document.createElement("img");
        img.alt = file.name || "Image preview";

        const caption = document.createElement("span");
        caption.textContent = "Primary";

        card.appendChild(radio);
        card.appendChild(img);
        card.appendChild(caption);

        const reader = new FileReader();
        reader.onload = (event) => {
            img.src = event.target.result;
        };
        reader.readAsDataURL(file);

        return card;
    };

    input.addEventListener("change", () => {
        clearPreview();
        const files = Array.from(input.files || []);
        if (!files.length) {
            return;
        }

        files.forEach((file, index) => {
            const card = createPreviewCard(file, index);
            container.appendChild(card);
        });
    });
};

document.addEventListener("DOMContentLoaded", () => {
    const hamburger = document.getElementById("admin-hamburger");
    const nav = document.getElementById("admin-nav");

    const imageInput = document.getElementById("variant-images");
    const previewContainer = document.getElementById("variant-image-preview");

    if (!hamburger || !nav) {
        if (imageInput && previewContainer) {
            setupImagePreview(imageInput, previewContainer);
        }
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

    if (imageInput && previewContainer) {
        setupImagePreview(imageInput, previewContainer);
    }
});

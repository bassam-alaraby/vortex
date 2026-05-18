const setupImagePreview = (input, container) => {
    let selectedFiles = [];
    let selectedPrimaryIndex = 1;

    const syncInputFiles = () => {
        const dataTransfer = new DataTransfer();
        selectedFiles.forEach((file) => dataTransfer.items.add(file));
        input.files = dataTransfer.files;
    };

    const getSelectedPrimaryFromDom = () => {
        const checkedRadio = container.querySelector('input[name="primary_upload"]:checked');
        if (!checkedRadio) {
            return null;
        }

        const value = Number.parseInt(checkedRadio.value, 10);
        return Number.isFinite(value) ? value : null;
    };

    const createPreviewCard = (file, index) => {
        const card = document.createElement("div");
        card.className = "image-card";

        const removeButton = document.createElement("button");
        removeButton.type = "button";
        removeButton.className = "image-remove-btn";
        removeButton.setAttribute("aria-label", `Remove image ${index + 1}`);
        removeButton.innerHTML = '<i class="ri-close-line" aria-hidden="true"></i>';
        removeButton.addEventListener("click", (event) => {
            event.preventDefault();
            event.stopPropagation();

            if (selectedPrimaryIndex === index + 1) {
                selectedPrimaryIndex = Math.max(1, Math.min(selectedPrimaryIndex, selectedFiles.length - 1));
            } else if (selectedPrimaryIndex > index + 1) {
                selectedPrimaryIndex -= 1;
            }

            selectedFiles = selectedFiles.filter((_, fileIndex) => fileIndex !== index);
            syncInputFiles();
            renderPreview();
        });

        const radio = document.createElement("input");
        radio.type = "radio";
        radio.name = "primary_upload";
        radio.value = String(index + 1);
        radio.className = "image-primary-radio";
        radio.checked = selectedPrimaryIndex === index + 1;
        radio.addEventListener("change", () => {
            selectedPrimaryIndex = index + 1;
        });

        const img = document.createElement("img");
        img.alt = file.name || "Image preview";

        const caption = document.createElement("span");
        caption.className = "image-primary-label";
        caption.textContent = "Primary";

        const footer = document.createElement("div");
        footer.className = "image-card-footer";
        footer.appendChild(caption);
        footer.appendChild(radio);

        card.appendChild(removeButton);
        card.appendChild(img);
        card.appendChild(footer);

        const reader = new FileReader();
        reader.onload = (event) => {
            img.src = event.target.result;
        };
        reader.readAsDataURL(file);

        return card;
    };

    const renderPreview = () => {
        const primaryFromDom = getSelectedPrimaryFromDom();
        if (primaryFromDom) {
            selectedPrimaryIndex = primaryFromDom;
        }

        container.innerHTML = "";

        if (!selectedFiles.length) {
            selectedPrimaryIndex = 1;
            return;
        }

        if (selectedPrimaryIndex > selectedFiles.length) {
            selectedPrimaryIndex = selectedFiles.length;
        }

        selectedFiles.forEach((file, index) => {
            const card = createPreviewCard(file, index);
            container.appendChild(card);
        });
    };

    input.addEventListener("change", () => {
        selectedFiles = Array.from(input.files || []);
        selectedPrimaryIndex = 1;
        renderPreview();
    });
};

document.addEventListener("DOMContentLoaded", () => {
    const hamburger = document.getElementById("admin-hamburger");
    const nav = document.getElementById("admin-nav");

    const imageInput = document.getElementById("variant-images");
    const previewContainer = document.getElementById("variant-image-preview");

    const setupUploadPreview = () => {
        if (!imageInput || !previewContainer) {
            return;
        }

        setupImagePreview(imageInput, previewContainer);
    };

    if (!hamburger || !nav) {
        setupUploadPreview();
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

    setupUploadPreview();
});

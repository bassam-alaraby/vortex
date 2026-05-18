document.addEventListener("DOMContentLoaded", () => {
    const fileInput = document.getElementById("custom-images");
    const previewList = document.getElementById("custom-preview-list");
    let selectedFiles = [];
    let currentObjectUrls = [];

    if (!fileInput || !previewList) {
        return;
    }

    const revokePreviewUrls = () => {
        currentObjectUrls.forEach((url) => URL.revokeObjectURL(url));
        currentObjectUrls = [];
    };

    const syncInputFiles = () => {
        const dataTransfer = new DataTransfer();
        selectedFiles.forEach((file) => dataTransfer.items.add(file));
        fileInput.files = dataTransfer.files;
    };

    const renderPreview = () => {
        revokePreviewUrls();
        previewList.innerHTML = "";

        if (!selectedFiles.length) {
            previewList.hidden = true;
            return;
        }

        selectedFiles.forEach((file, index) => {
            const objectUrl = URL.createObjectURL(file);
            currentObjectUrls.push(objectUrl);

            const card = document.createElement("div");
            card.className = "custom-preview-card";

            const preview = document.createElement("img");
            preview.className = "custom-preview";
            preview.src = objectUrl;
            preview.alt = `معاينة التصميم ${index + 1}`;

            const removeButton = document.createElement("button");
            removeButton.type = "button";
            removeButton.className = "custom-preview-remove";
            removeButton.setAttribute("aria-label", `إزالة الصورة ${index + 1}`);
            removeButton.innerHTML = '<i class="ri-close-line" aria-hidden="true"></i>';
            removeButton.addEventListener("click", () => {
                selectedFiles = selectedFiles.filter((_, fileIndex) => fileIndex !== index);
                syncInputFiles();
                renderPreview();
            });

            card.appendChild(preview);
            card.appendChild(removeButton);
            previewList.appendChild(card);
        });

        previewList.hidden = false;
    };

    fileInput.addEventListener("change", () => {
        selectedFiles = Array.from(fileInput.files || []);
        renderPreview();
    });
});

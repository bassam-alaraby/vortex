document.addEventListener("DOMContentLoaded", () => {
    const fileInput = document.getElementById("custom-image");
    const preview = document.getElementById("custom-preview");
    const clearButton = document.getElementById("custom-image-clear");
    let currentObjectUrl = null;

    if (!fileInput || !preview) {
        return;
    }

    const resetPreview = () => {
        if (currentObjectUrl) {
            URL.revokeObjectURL(currentObjectUrl);
            currentObjectUrl = null;
        }

        fileInput.value = "";
        preview.hidden = true;
        preview.removeAttribute("src");
    };

    fileInput.addEventListener("change", () => {
        const file = fileInput.files && fileInput.files[0];

        if (!file) {
            resetPreview();
            return;
        }

        if (currentObjectUrl) {
            URL.revokeObjectURL(currentObjectUrl);
        }

        currentObjectUrl = URL.createObjectURL(file);
        preview.src = currentObjectUrl;
        preview.hidden = false;
    });

    if (clearButton) {
        clearButton.addEventListener("click", resetPreview);
    }
});

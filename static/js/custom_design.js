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

    const productForm = document.querySelector(".custom-design-page .product-info");
    if (!productForm) {
        return;
    }

    productForm.addEventListener("submit", async (e) => {
        if (e.submitter?.value !== "buy_now") return;

        e.preventDefault();

        const submitButton = e.submitter;
        const originalText = submitButton.textContent;
        submitButton.disabled = true;
        submitButton.textContent = "جاري رفع التصميم...";
        window.VortexUI?.disableFormSubmit(productForm, submitButton);
        showCustomDesignMessage(productForm, "", false);

        try {
            const actionUrl = productForm.getAttribute("action") || window.location.pathname;
            const formData = new FormData(productForm);
            formData.append(submitButton.name, submitButton.value);

            const response = await fetch(actionUrl, {
                method: "POST",
                body: formData,
                headers: {
                    "X-Requested-With": "XMLHttpRequest",
                    "X-CSRFToken": getCustomDesignCsrfToken()
                }
            });

            const data = await response.json().catch(() => null);

            if (!response.ok || !data?.success) {
                showCustomDesignMessage(
                    productForm,
                    data?.message || "تعذر إرسال التصميم، يرجى مراجعة البيانات.",
                    true
                );
                return;
            }

            window.VortexUI?.updateCartBadge(data.cart_count);
            window.VortexCheckout?.open();
        } catch (error) {
            console.error("Custom buy now failed:", error);
            submitCustomDesignFallback(productForm, "buy_now");
        } finally {
            window.VortexUI?.enableFormSubmit(productForm);
            submitButton.disabled = false;
            submitButton.textContent = originalText;
        }
    });
});

function getCustomDesignCsrfToken() {
    return document.querySelector('meta[name="csrf-token"]')?.content || "";
}

function showCustomDesignMessage(form, message, isError) {
    let messageNode = form.querySelector("[data-custom-design-message]");
    if (!messageNode) {
        messageNode = document.createElement("p");
        messageNode.setAttribute("data-custom-design-message", "");
        messageNode.setAttribute("aria-live", "polite");
        form.querySelector(".product-actions")?.before(messageNode);
    }

    messageNode.textContent = message;
    messageNode.classList.toggle("error", isError);
}

function submitCustomDesignFallback(form, action) {
    const actionInput = document.createElement("input");
    actionInput.type = "hidden";
    actionInput.name = "action";
    actionInput.value = action;
    form.appendChild(actionInput);
    form.submit();
}

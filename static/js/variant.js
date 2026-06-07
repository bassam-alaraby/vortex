document.addEventListener("DOMContentLoaded", () => {
    const productForm = document.querySelector(".variant .product-info");
    if (!productForm) {
        return;
    }

    const sizeInput = productForm.querySelector("#selected-size");
    const qtyInput = productForm.querySelector("#selected-qty");

    const sizeButtons = productForm.querySelectorAll(".size-selector .btn");
    sizeButtons.forEach((button) => {
        button.addEventListener("click", () => {
            sizeButtons.forEach((btn) => btn.classList.remove("active"));
            button.classList.add("active");

            if (sizeInput) {
                sizeInput.value = button.textContent.trim();
            }
        });
    });

    const activeSizeButton = productForm.querySelector(".size-selector .btn.active");
    if (activeSizeButton && sizeInput) {
        sizeInput.value = activeSizeButton.textContent.trim();
    }

    const qtyDisplay = productForm.querySelector(".qty-display");
    const plusBtn = productForm.querySelector(".ri-add-line")?.parentElement;
    const minusBtn = productForm.querySelector(".ri-subtract-line")?.parentElement;

    if (!qtyDisplay) {
        return;
    }

    let quantity = parseInt(qtyDisplay.textContent, 10) || 1;

    if (plusBtn) {
        plusBtn.addEventListener("click", () => {
            quantity += 1;
            qtyDisplay.textContent = quantity;
            if (qtyInput) {
                qtyInput.value = quantity;
            }
        });
    }

    if (minusBtn) {
        minusBtn.addEventListener("click", () => {
            if (quantity <= 1) {
                return;
            }

            quantity -= 1;
            qtyDisplay.textContent = quantity;
            if (qtyInput) {
                qtyInput.value = quantity;
            }
        });
    }

    productForm.addEventListener("submit", async (e) => {
        if (e.submitter?.value !== "buy_now") return;
        if (!productForm.querySelector('[name="variant_id"]')) return;

        e.preventDefault();

        const submitButton = e.submitter;
        const originalText = submitButton.textContent;
        submitButton.disabled = true;
        submitButton.textContent = "جاري التجهيز...";
        window.VortexUI?.disableFormSubmit(productForm, submitButton);
        showVariantFormMessage(productForm, "", false);

        try {
            const formData = new FormData(productForm);
            formData.append(submitButton.name, submitButton.value);

            const response = await fetch("/add_to_cart", {
                method: "POST",
                body: formData,
                headers: {
                    "X-Requested-With": "XMLHttpRequest",
                    "X-CSRFToken": getVariantCsrfToken()
                }
            });

            const data = await response.json().catch(() => null);

            if (!response.ok || !data?.success) {
                showVariantFormMessage(
                    productForm,
                    data?.message || "تعذر إضافة المنتج، يرجى مراجعة الاختيارات.",
                    true
                );
                return;
            }

            window.VortexUI?.updateCartBadge(data.cart_count);
            window.VortexCheckout?.open();
        } catch (error) {
            console.error("Buy now failed:", error);
            submitFormFallback(productForm, "buy_now");
        } finally {
            window.VortexUI?.enableFormSubmit(productForm);
            submitButton.disabled = false;
            submitButton.textContent = originalText;
        }
    });
});

function getVariantCsrfToken() {
    return document.querySelector('meta[name="csrf-token"]')?.content || "";
}

function showVariantFormMessage(form, message, isError) {
    let messageNode = form.querySelector("[data-product-form-message]");
    if (!messageNode) {
        messageNode = document.createElement("p");
        messageNode.setAttribute("data-product-form-message", "");
        messageNode.setAttribute("aria-live", "polite");
        form.querySelector(".product-actions")?.before(messageNode);
    }

    messageNode.textContent = message;
    messageNode.classList.toggle("error", isError);
}

function submitFormFallback(form, action) {
    const actionInput = document.createElement("input");
    actionInput.type = "hidden";
    actionInput.name = "action";
    actionInput.value = action;
    form.appendChild(actionInput);
    form.submit();
}

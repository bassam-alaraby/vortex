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
});

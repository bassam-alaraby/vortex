function updateCartTotal(total) {
    const totalValue = document.querySelector(".summary-total .value");
    if (totalValue) {
        totalValue.textContent = `${total} ج.م`;
    }
}

function getCsrfToken() {
    return document.querySelector('meta[name="csrf-token"]')?.getAttribute("content") || "";
}

function setCardPending(card, isPending) {
    card.style.pointerEvents = isPending ? "none" : "auto";
    card.style.opacity = isPending ? "0.65" : "1";
}

async function sendCartUpdate(payload) {
    const csrfToken = getCsrfToken();
    const response = await fetch("/update_cart", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrfToken
        },
        body: JSON.stringify(payload)
    });

    const data = await response.json().catch(() => null);
    if (!response.ok || !data?.success) {
        throw new Error(data?.message || "Cart update failed");
    }

    return data;
}

function bindQuantityControls(card) {
    const qtyDisplay = card.querySelector(".qty-display");
    const buttons = card.querySelectorAll(".quantity-selector .btn");
    const minusBtn = buttons[0];
    const plusBtn = buttons[1];

    if (!qtyDisplay || !minusBtn || !plusBtn) {
        return;
    }

    minusBtn.addEventListener("click", async () => {
        const quantity = parseInt(qtyDisplay.textContent, 10) || 1;
        if (quantity <= 1 || card.dataset.pending === "true") {
            return;
        }

        await updateCartItem(card, { quantity: quantity - 1 });
    });

    plusBtn.addEventListener("click", async () => {
        const quantity = parseInt(qtyDisplay.textContent, 10) || 1;
        if (card.dataset.pending === "true") {
            return;
        }

        await updateCartItem(card, { quantity: quantity + 1 });
    });
}

function bindRemoveButton(card) {
    const removeButton = card.querySelector(".remove-btn");
    if (!removeButton) {
        return;
    }

    removeButton.addEventListener("click", async () => {
        if (card.dataset.pending === "true") {
            return;
        }

        await updateCartItem(card, { quantity: 0 });
    });
}

function bindSizeControls(card) {
    const sizeButtons = card.querySelectorAll(".size-selector [data-size-option]");
    sizeButtons.forEach((button) => {
        button.addEventListener("click", async () => {
            const newSize = button.dataset.sizeOption;
            if (!newSize || newSize === card.dataset.size || card.dataset.pending === "true") {
                return;
            }

            await updateCartItem(card, {
                quantity: parseInt(card.querySelector(".qty-display")?.textContent || "1", 10),
                newSize
            });
        });
    });
}

function setActiveSize(card, activeSize) {
    card.querySelectorAll(".size-selector [data-size-option]").forEach((button) => {
        button.classList.toggle("active", button.dataset.sizeOption === activeSize);
    });
}

function parsePrice(text) {
    const numeric = String(text || "").replace(/[^\d.]/g, "");
    const value = Number(numeric);
    return Number.isFinite(value) ? value : 0;
}

function formatPrice(value) {
    return `${Math.round(value)} ج.م`;
}

function renderCheckoutSummary() {
    const checkoutForm = document.getElementById("checkout-form");
    const summaryList = document.getElementById("checkout-summary-items");
    const emptyState = document.getElementById("checkout-summary-empty");
    const totalNode = document.getElementById("checkout-summary-total");
    const feeNode = document.getElementById("checkout-summary-fee");
    const deliverySelect = document.getElementById("delivery-region");
    const deliveryHidden = document.getElementById("delivery-region-hidden");
    const submitButton = document.querySelector(".checkout-form__submit");

    if (!summaryList || !emptyState || !totalNode) {
        return;
    }

    const cards = Array.from(document.querySelectorAll(".cart-card"));
    summaryList.innerHTML = "";

    if (!cards.length) {
        emptyState.hidden = false;
        totalNode.textContent = formatPrice(0);
        if (feeNode) {
            feeNode.textContent = formatPrice(0);
        }
        if (submitButton) {
            submitButton.disabled = true;
        }
        return;
    }

    emptyState.hidden = true;

    let total = 0;

    cards.forEach((card) => {
        const name = card.querySelector(".product-header h2")?.textContent?.trim() || "منتج";
        const size = card.dataset.size || "-";
        const quantity = parseInt(card.querySelector(".qty-display")?.textContent || "1", 10) || 1;
        const unitPrice = parsePrice(card.querySelector(".product-price span")?.textContent || "0");
        const lineTotal = unitPrice * quantity;
        total += lineTotal;

        const row = document.createElement("li");
        row.className = "checkout-summary-item";

        const meta = document.createElement("div");
        meta.className = "checkout-summary-item__meta";

        const title = document.createElement("strong");
        title.textContent = `${name} - ${size}`;

        const details = document.createElement("span");
        details.textContent = `الكمية: ${quantity}`;

        meta.appendChild(title);
        meta.appendChild(details);

        const price = document.createElement("span");
        price.className = "checkout-summary-item__price";
        price.textContent = formatPrice(lineTotal);

        row.appendChild(meta);
        row.appendChild(price);
        summaryList.appendChild(row);
    });

    const selectedOption = deliverySelect?.selectedOptions?.[0];
    const deliveryFee = selectedOption ? parsePrice(selectedOption.dataset.fee) : 0;
    if (feeNode) {
        feeNode.textContent = formatPrice(deliveryFee);
    }

    totalNode.textContent = formatPrice(total + deliveryFee);

    if (deliveryHidden) {
        deliveryHidden.value = deliverySelect?.value || "";
    }

    if (submitButton) {
        submitButton.disabled = !deliverySelect?.value;
    }

    if (!deliverySelect?.value && deliverySelect) {
        setCheckoutFieldError(checkoutForm, "delivery_region", "يرجى اختيار منطقة الشحن.");
    }
}

function normalizeSpaces(value) {
    return String(value || "").trim().replace(/\s+/g, " ");
}

function normalizePhone(value) {
    return String(value || "")
        .trim()
        .replace(/[٠-٩]/g, (digit) => String(digit.charCodeAt(0) - 1632))
        .replace(/[۰-۹]/g, (digit) => String(digit.charCodeAt(0) - 1776))
        .replace(/\s+/g, "");
}

function clearCheckoutFieldErrors(form) {
    form.querySelectorAll("[data-field]").forEach((field) => {
        field.classList.remove("checkout-field-invalid");
        field.removeAttribute("aria-invalid");
    });

    form.querySelectorAll("[data-error-for]").forEach((errorNode) => {
        errorNode.textContent = "";
    });

    const deliveryField = document.querySelector('[data-field="delivery_region"]');
    if (deliveryField) {
        deliveryField.classList.remove("checkout-field-invalid");
        deliveryField.removeAttribute("aria-invalid");
    }

    const deliveryError = document.querySelector('[data-error-for="delivery_region"]');
    if (deliveryError) {
        deliveryError.textContent = "";
    }
}

function setCheckoutFieldError(form, fieldName, message) {
    const field = form?.querySelector(`[data-field="${fieldName}"]`)
        || document.querySelector(`[data-field="${fieldName}"]`);
    const errorNode = form?.querySelector(`[data-error-for="${fieldName}"]`)
        || document.querySelector(`[data-error-for="${fieldName}"]`);

    if (field) {
        if (message) {
            field.classList.add("checkout-field-invalid");
            field.setAttribute("aria-invalid", "true");
        } else {
            field.classList.remove("checkout-field-invalid");
            field.removeAttribute("aria-invalid");
        }
    }

    if (errorNode) {
        errorNode.textContent = message;
    }
}

function validateCheckoutForm(form) {
    const values = {
        name: normalizeSpaces(form.querySelector('[name="name"]')?.value),
        phone: normalizePhone(form.querySelector('[name="phone"]')?.value),
        address: normalizeSpaces(form.querySelector('[name="address"]')?.value),
        notes: normalizeSpaces(form.querySelector('[name="notes"]')?.value),
        deliveryRegion: (document.getElementById("delivery-region")?.value || "").trim()
    };

    const errors = {};
    const namePattern = /^[A-Za-z\u0600-\u06FF\s]+$/;

    if (!values.name) {
        errors.name = "يرجى إدخال الاسم.";
    } else if (values.name.length < 2) {
        errors.name = "الاسم قصير جدًا.";
    } else if (values.name.length > 60) {
        errors.name = "الاسم طويل جدًا.";
    } else if (!namePattern.test(values.name)) {
        errors.name = "الاسم يجب أن يحتوي على حروف ومسافات فقط.";
    }

    if (!values.phone) {
        errors.phone = "يرجى إدخال رقم الهاتف.";
    } else if (!/^\d+$/.test(values.phone)) {
        errors.phone = "رقم الهاتف يجب أن يحتوي على أرقام فقط.";
    } else if (values.phone.length < 8 || values.phone.length > 15) {
        errors.phone = "رقم الهاتف يجب أن يكون من 8 إلى 15 رقمًا.";
    }

    if (!values.address) {
        errors.address = "يرجى إدخال العنوان.";
    } else if (values.address.length < 8) {
        errors.address = "العنوان قصير جدًا.";
    } else if (values.address.length > 220) {
        errors.address = "العنوان طويل جدًا.";
    }

    if (values.notes.length > 500) {
        errors.notes = "الملاحظات يجب ألا تتجاوز 500 حرف.";
    }

    if (!values.deliveryRegion) {
        errors.delivery_region = "يرجى اختيار منطقة الشحن.";
    }

    return {
        values,
        errors,
        isValid: Object.keys(errors).length === 0
    };
}

function setupCheckoutModal() {
    const checkoutModal = document.getElementById("checkout-modal");
    const openButton = document.querySelector("[data-open-checkout-modal]");
    const closeButtons = document.querySelectorAll("[data-close-checkout-modal]");
    const checkoutForm = document.getElementById("checkout-form");
    const feedback = document.getElementById("checkout-feedback");
    const deliverySelect = document.getElementById("delivery-region");

    if (!checkoutModal || !openButton || !checkoutForm || !feedback) {
        return;
    }

    const checkoutUrl = checkoutForm.getAttribute("action") || "/checkout";

    const submitButton = checkoutForm.querySelector(".checkout-form__submit");

    function openModal() {
        renderCheckoutSummary();
        clearCheckoutFieldErrors(checkoutForm);
        showFeedback("", false);
        checkoutModal.hidden = false;
        document.body.classList.add("checkout-open");
    }

    function closeModal() {
        checkoutModal.hidden = true;
        document.body.classList.remove("checkout-open");
    }

    function showFeedback(message, isError) {
        feedback.textContent = message;
        feedback.classList.toggle("error", isError);
        feedback.classList.toggle("success", !isError);
    }

    openButton.addEventListener("click", openModal);

    closeButtons.forEach((button) => {
        button.addEventListener("click", closeModal);
    });

    document.addEventListener("keydown", (event) => {
        if (event.key === "Escape" && !checkoutModal.hidden) {
            closeModal();
        }
    });

    const params = new URLSearchParams(window.location.search);
    if (params.get("open_checkout") === "1") {
        openModal();
    }

    if (deliverySelect) {
        deliverySelect.addEventListener("change", () => {
            setCheckoutFieldError(checkoutForm, "delivery_region", "");
            renderCheckoutSummary();
        });
    }

    checkoutForm.addEventListener("submit", async (event) => {
        event.preventDefault();

        window.VortexUI?.disableFormSubmit(checkoutForm);

        clearCheckoutFieldErrors(checkoutForm);
        showFeedback("", false);

        const validation = validateCheckoutForm(checkoutForm);
        if (!validation.isValid) {
            Object.entries(validation.errors).forEach(([fieldName, message]) => {
                setCheckoutFieldError(checkoutForm, fieldName, message);
            });
            showFeedback("يرجى مراجعة البيانات المدخلة.", true);
            window.VortexUI?.enableFormSubmit(checkoutForm);
            return;
        }

        checkoutForm.querySelector('[name="name"]').value = validation.values.name;
        checkoutForm.querySelector('[name="phone"]').value = validation.values.phone;
        checkoutForm.querySelector('[name="address"]').value = validation.values.address;
        checkoutForm.querySelector('[name="notes"]').value = validation.values.notes;
        const deliveryHidden = document.getElementById("delivery-region-hidden");
        if (deliveryHidden) {
            deliveryHidden.value = validation.values.deliveryRegion;
        }

        if (submitButton) {
            submitButton.textContent = "جاري تأكيد الطلب...";
        }

        try {
            const csrfToken = getCsrfToken();
            const response = await fetch(checkoutUrl, {
                method: "POST",
                body: new FormData(checkoutForm),
                headers: {
                    "X-Requested-With": "XMLHttpRequest",
                    "X-CSRFToken": csrfToken
                }
            });

            const data = await response.json().catch(() => null);

            if (!response.ok || !data?.success) {
                if (data?.errors && typeof data.errors === "object") {
                    Object.entries(data.errors).forEach(([fieldName, message]) => {
                        setCheckoutFieldError(checkoutForm, fieldName, message);
                    });
                }
                throw new Error(data?.message || "تعذر إرسال الطلب، حاول مرة أخرى.");
            }

            showFeedback(
                data.message || "تم استلام طلبك بنجاح، سيتم التواصل معك قريبًا.",
                false
            );

            window.VortexUI?.updateCartBadge(0);

            window.setTimeout(() => {
                window.location.href = "/cart";
            }, 1300);
        } catch (error) {
            console.error("Checkout failed:", error);
            showFeedback(error.message, true);
            window.VortexUI?.enableFormSubmit(checkoutForm);

            if (submitButton) {
                submitButton.textContent = "تأكيد الطلب";
            }
        }
    });
}

async function updateCartItem(card, changes) {
    const currentSize = card.dataset.size;
    const quantity = changes.quantity;
    const payload = {
        variant_id: Number(card.dataset.variantId),
        size: currentSize,
        quantity,
        cart_item_id: card.dataset.cartItemId
    };

    if (changes.newSize) {
        payload.new_size = changes.newSize;
    }

    card.dataset.pending = "true";
    setCardPending(card, true);

    try {
        const data = await sendCartUpdate(payload);

        updateCartTotal(data.total);
        window.VortexUI?.updateCartBadge(data.cart_count);

        if (data.removed) {
            card.remove();
            renderCheckoutSummary();

            if (!document.querySelector(".cart-card")) {
                window.location.reload();
            }
            return;
        }

        if (data.merged && changes.newSize) {
            const mergedTarget = document.querySelector(
                `.cart-card[data-cart-item-id="${data.item.cart_item_id}"]`
            );

            if (mergedTarget && mergedTarget !== card) {
                mergedTarget.querySelector(".qty-display").textContent = data.item.quantity;
                card.remove();
            } else {
                card.dataset.size = data.item.size;
                card.dataset.cartItemId = data.item.cart_item_id;
                card.querySelector(".qty-display").textContent = data.item.quantity;
                setActiveSize(card, data.item.size);
            }

            renderCheckoutSummary();
            return;
        }

        card.dataset.size = data.item.size;
        card.dataset.cartItemId = data.item.cart_item_id;
        card.querySelector(".qty-display").textContent = data.item.quantity;
        setActiveSize(card, data.item.size);
        renderCheckoutSummary();
    } catch (error) {
        console.error("Cart update failed:", error);
    } finally {
        delete card.dataset.pending;
        if (document.body.contains(card)) {
            setCardPending(card, false);
        }
    }
}

document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll(".cart-card").forEach((card) => {
        bindQuantityControls(card);
        bindRemoveButton(card);
        bindSizeControls(card);
    });

    setupCheckoutModal();
    renderCheckoutSummary();
});

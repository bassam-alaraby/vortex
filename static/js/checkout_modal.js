function getCsrfToken() {
    return document.querySelector('meta[name="csrf-token"]')?.getAttribute("content") || "";
}

function formatPrice(value) {
    return `${Math.round(value)} ج.م`;
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

function resetCheckoutSummary() {
    const summaryList = document.getElementById("checkout-summary-items");
    const emptyState = document.getElementById("checkout-summary-empty");
    const totalNode = document.getElementById("checkout-summary-total");
    const feeNode = document.getElementById("checkout-summary-fee");
    const submitButton = document.querySelector(".checkout-form__submit");

    if (summaryList) {
        summaryList.innerHTML = "";
    }
    if (emptyState) {
        emptyState.hidden = false;
    }
    if (feeNode) {
        feeNode.textContent = formatPrice(0);
    }
    if (totalNode) {
        totalNode.textContent = formatPrice(0);
    }
    if (submitButton) {
        submitButton.disabled = true;
    }
}

async function renderCheckoutSummary() {
    try {
        const res = await fetch('/api/cart_summary');
        if (!res.ok) throw new Error('cart summary failed');
        const data = await res.json();
        renderItems(data.items || []);
    } catch (err) {
        console.error('[VortexCheckout] renderCheckoutSummary error:', err);
        resetCheckoutSummary();
    }
}

function renderItems(items) {
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

    summaryList.innerHTML = "";

    if (!items.length) {
        emptyState.hidden = false;
        totalNode.textContent = formatPrice(0);
        if (feeNode) {
            feeNode.textContent = formatPrice(0);
        }
        if (deliveryHidden) {
            deliveryHidden.value = deliverySelect?.value || "";
        }
        if (submitButton) {
            submitButton.disabled = true;
        }
        return;
    }

    emptyState.hidden = true;

    let subtotal = 0;

    items.forEach((item) => {
        const name = item.name || "منتج";
        const size = item.size || "-";
        const quantity = parseInt(item.quantity, 10) || 1;
        const unitPrice = parseFloat(item.unit_price) || 0;
        const lineTotal = unitPrice * quantity;
        subtotal += lineTotal;

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
    const deliveryFee = selectedOption ? parseFloat(selectedOption.dataset.fee) || 0 : 0;
    if (feeNode) {
        feeNode.textContent = formatPrice(deliveryFee);
    }

    totalNode.textContent = formatPrice(subtotal + deliveryFee);

    if (deliveryHidden) {
        deliveryHidden.value = deliverySelect?.value || "";
    }

    if (submitButton) {
        submitButton.disabled = !deliverySelect?.value;
    }
}

function setupCheckoutModal() {
    const checkoutForm = document.getElementById("checkout-form");
    if (checkoutForm?.dataset.checkoutBound === 'true') return;
    if (checkoutForm) checkoutForm.dataset.checkoutBound = 'true';

    const checkoutModal = document.getElementById("checkout-modal");
    const openButton = document.querySelector("[data-open-checkout-modal]");
    const closeButtons = document.querySelectorAll("[data-close-checkout-modal]");
    const feedback = document.getElementById("checkout-feedback");
    const deliverySelect = document.getElementById("delivery-region");

    if (!checkoutModal || !checkoutForm || !feedback) {
        return;
    }

    const checkoutUrl = checkoutForm.getAttribute("action") || "/checkout";

    const submitButton = checkoutForm.querySelector(".checkout-form__submit");

    async function openModal() {
        await renderCheckoutSummary();
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

    if (openButton) {
        openButton.addEventListener("click", openModal);
    }

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
                window.location.href = "/collection";
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

    window.VortexCheckout = {
        open:          openModal,
        close:         closeModal,
        renderSummary: renderCheckoutSummary,
    };
}

document.addEventListener('DOMContentLoaded', setupCheckoutModal);

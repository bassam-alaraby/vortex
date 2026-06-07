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
            window.VortexCheckout?.renderSummary();

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

            window.VortexCheckout?.renderSummary();
            return;
        }

        card.dataset.size = data.item.size;
        card.dataset.cartItemId = data.item.cart_item_id;
        card.querySelector(".qty-display").textContent = data.item.quantity;
        setActiveSize(card, data.item.size);
        window.VortexCheckout?.renderSummary();
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
});

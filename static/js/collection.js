document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll("form[data-ajax-add-to-cart='true']").forEach((form) => {
        const submitButton = form.querySelector(".add-to-cart");
        const submitUrl = form.getAttribute("action") || "/add_to_cart";
        if (!submitButton) {
            return;
        }

        let resetTimerId;

        form.addEventListener("submit", async (event) => {
            event.preventDefault();

            if (submitButton.disabled) {
                return;
            }

            const originalText = submitButton.dataset.originalText || submitButton.textContent;
            submitButton.dataset.originalText = originalText;
            submitButton.disabled = true;
            submitButton.textContent = "Adding...";

            window.clearTimeout(resetTimerId);

            const restoreButton = () => {
                submitButton.textContent = originalText;
                submitButton.classList.remove("is-added");
                submitButton.disabled = false;
            };

            try {
                const response = await fetch(submitUrl, {
                    method: "POST",
                    body: new FormData(form),
                    headers: {
                        "X-Requested-With": "XMLHttpRequest"
                    }
                });

                const data = await response.json().catch(() => null);

                if (!response.ok || !data?.success) {
                    throw new Error(data?.message || "Could not add item to cart");
                }

                window.VortexUI?.updateCartBadge(data.cart_count);

                submitButton.textContent = "Added";
                submitButton.classList.add("is-added");

                resetTimerId = window.setTimeout(() => {
                    restoreButton();
                }, 1200);
            } catch (error) {
                console.error("Collection add-to-cart failed:", error);
                submitButton.textContent = "Try again";

                resetTimerId = window.setTimeout(() => {
                    restoreButton();
                }, 1200);
            }
        });
    });
});

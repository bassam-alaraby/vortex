const SUBMIT_LOCK_ATTR = "submitLocked";
const SUBMIT_PREV_DISABLED_ATTR = "submitGuardPrevDisabled";
const SUBMIT_CONTROL_SELECTOR = "button[type='submit'], input[type='submit']";

function getSubmitControls(form) {
    return Array.from(form.querySelectorAll(SUBMIT_CONTROL_SELECTOR));
}

function disableFormSubmit(form) {
    if (!(form instanceof HTMLFormElement)) {
        return;
    }

    form.dataset[SUBMIT_LOCK_ATTR] = "true";

    getSubmitControls(form).forEach((control) => {
        control.dataset[SUBMIT_PREV_DISABLED_ATTR] = control.disabled ? "1" : "0";
        control.disabled = true;
        control.setAttribute("aria-disabled", "true");
    });
}

function enableFormSubmit(form) {
    if (!(form instanceof HTMLFormElement)) {
        return;
    }

    delete form.dataset[SUBMIT_LOCK_ATTR];

    getSubmitControls(form).forEach((control) => {
        const wasDisabled = control.dataset[SUBMIT_PREV_DISABLED_ATTR] === "1";
        control.disabled = wasDisabled;
        control.removeAttribute("aria-disabled");
        delete control.dataset[SUBMIT_PREV_DISABLED_ATTR];
    });
}

document.addEventListener("submit", (event) => {
    const form = event.target;
    if (!(form instanceof HTMLFormElement)) {
        return;
    }

    if (form.dataset[SUBMIT_LOCK_ATTR] === "true") {
        event.preventDefault();
        return;
    }

    disableFormSubmit(form);

    window.setTimeout(() => {
        if (event.defaultPrevented) {
            enableFormSubmit(form);
        }
    }, 0);
});

window.VortexUI = window.VortexUI || {};
window.VortexUI.disableFormSubmit = disableFormSubmit;
window.VortexUI.enableFormSubmit = enableFormSubmit;

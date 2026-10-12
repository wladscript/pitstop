/**
 * Pit Stop - Sistema leve de Toasts nativos em Vanilla JS
 */

function showToast(message, type = "info", duration = 4000) {
    let container = document.querySelector(".toast-container");
    if (!container) {
        container = document.createElement("div");
        container.className = "toast-container";
        document.body.appendChild(container);
    }

    const toast = document.createElement("div");
    toast.className = `toast toast-${type}`;

    const iconMap = {
        success: "✔",
        error: "✖",
        warning: "⚠",
        info: "ℹ",
    };

    toast.innerHTML = `
        <span style="font-weight: 800;">${iconMap[type] || "•"}</span>
        <span style="flex: 1;">${message}</span>
    `;

    container.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = "0";
        toast.style.transform = "translateY(-10px)";
        toast.style.transition = "all 0.3s ease";
        setTimeout(() => toast.remove(), 300);
    }, duration);
}

// Inicializar toasts que vieram das mensagens do Django na renderização
document.addEventListener("DOMContentLoaded", () => {
    const djangoMessages = document.querySelectorAll("[data-django-message]");
    djangoMessages.forEach((el) => {
        const text = el.getAttribute("data-django-message");
        const tag = el.getAttribute("data-django-tag") || "info";
        showToast(text, tag);
        el.remove();
    });
});

window.showToast = showToast;

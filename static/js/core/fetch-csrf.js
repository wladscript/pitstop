/**
 * Pit Stop - Utilitário de requisições Fetch autenticadas com CSRF do Django
 */

function getCsrfToken() {
    const metaTag = document.querySelector('meta[name="csrf-token"]');
    if (metaTag) return metaTag.getAttribute("content");

    const inputTag = document.querySelector('input[name="csrfmiddlewaretoken"]');
    if (inputTag) return inputTag.value;

    const cookieMatch = document.cookie.match(/csrftoken=([^;]+)/);
    return cookieMatch ? cookieMatch[1] : "";
}

async function fetchJson(url, options = {}) {
    const headers = {
        "Content-Type": "application/json",
        "X-CSRFToken": getCsrfToken(),
        "X-Requested-With": "XMLHttpRequest",
        ...(options.headers || {}),
    };

    const response = await fetch(url, {
        ...options,
        headers,
    });

    const data = await response.json().catch(() => ({}));
    if (!response.ok) {
        const error = new Error(data.error || data.detail || `Erro na requisição (${response.status})`);
        error.status = response.status;
        error.data = data;
        throw error;
    }

    return data;
}

window.getCsrfToken = getCsrfToken;
window.fetchJson = fetchJson;

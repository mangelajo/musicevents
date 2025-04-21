function setCookie(name, value, days) {
    let expires = "";
    if (days) {
        const date = new Date();
        date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
        expires = "; expires=" + date.toUTCString();
    }
    document.cookie = name + "=" + (value || "") + expires + "; path=/";
}

function getCookie(name) {
    const nameEQ = name + "=";
    const ca = document.cookie.split(';');
    for(let i = 0; i < ca.length; i++) {
        let c = ca[i];
        while (c.charAt(0) === ' ') {
            c = c.substring(1, c.length);
        }
        if (c.indexOf(nameEQ) === 0) {
            return c.substring(nameEQ.length, c.length);
        }
    }
    return null;
}

function showCookieConsent() {
    if (!getCookie('cookieConsent')) {
        const consentBanner = document.getElementById('cookie-consent-banner');
        if (consentBanner) {
            consentBanner.style.display = 'block';
        }
    }
}

function acceptCookies() {
    setCookie('cookieConsent', 'accepted', 365);
    const consentBanner = document.getElementById('cookie-consent-banner');
    if (consentBanner) {
        consentBanner.style.display = 'none';
    }
}

// Show the cookie consent banner when the page loads
document.addEventListener('DOMContentLoaded', showCookieConsent);
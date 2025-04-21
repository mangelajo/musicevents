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
        const overlay = document.getElementById('cookie-consent-overlay');
        const modal = document.getElementById('cookie-consent-modal');
        const body = document.body;

        if (overlay && modal) {
            overlay.style.display = 'block';
            modal.style.display = 'block';
            body.classList.add('cookie-consent-active');

            // Prevent scrolling on the background
            body.style.overflow = 'hidden';

            // Disable all interactive elements outside the modal
            const interactiveElements = document.querySelectorAll('a, button, input, select, textarea');
            interactiveElements.forEach(element => {
                if (!modal.contains(element)) {
                    element.setAttribute('tabindex', '-1');
                    element.setAttribute('aria-hidden', 'true');
                }
            });
        }
    }
}

function acceptCookies() {
    setCookie('cookieConsent', 'accepted', 365);
    const overlay = document.getElementById('cookie-consent-overlay');
    const modal = document.getElementById('cookie-consent-modal');
    const body = document.body;

    if (overlay && modal) {
        overlay.style.display = 'none';
        modal.style.display = 'none';
        body.classList.remove('cookie-consent-active');

        // Re-enable scrolling
        body.style.overflow = '';

        // Re-enable all interactive elements
        const interactiveElements = document.querySelectorAll('a, button, input, select, textarea');
        interactiveElements.forEach(element => {
            element.removeAttribute('tabindex');
            element.removeAttribute('aria-hidden');
        });
    }
}

// Show the cookie consent modal when the page loads
document.addEventListener('DOMContentLoaded', showCookieConsent);
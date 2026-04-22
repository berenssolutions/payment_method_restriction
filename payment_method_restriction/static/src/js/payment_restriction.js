/** @odoo-module **/
/**
 * payment_method_restriction/static/src/js/payment_restriction.js
 *
 * Blendet Zahlungsanbieter-Kacheln im eCommerce-Checkout aus,
 * wenn mindestens ein Artikel im Warenkorb eine Sperre für diesen
 * Anbieter gesetzt hat.
 *
 * Ablauf:
 *  1. Beim Laden der Checkout-Seite JSON-Endpunkt abfragen.
 *  2. Für jede zurückgegebene Provider-ID das zugehörige DOM-Element
 *     mit data-provider-id="<id>" ausblenden.
 *  3. Falls alle Provider gesperrt sind, eine Hinweismeldung anzeigen.
 *
 * Autor: Lennart Berens, Berens Solutions <mail@berenssolutions.de>
 */

import { rpc } from "@web/core/network/rpc";
import { onMounted } from "@odoo/owl";

// Sicherstellen, dass wir nur auf der Checkout/Payment-Seite aktiv werden
const PAYMENT_PAGE_SELECTOR = '#payment_method';

/**
 * Blendet einen einzelnen Zahlungsanbieter-Block aus.
 *
 * Odoo 18 rendert Payment-Provider in Containern mit dem Attribut
 * data-provider-id="<id>" innerhalb von #payment_method.
 *
 * @param {number} providerId
 */
function hideProvider(providerId) {
    // Primärer Selektor für Odoo 18 Payment-Widgets
    const selectors = [
        `[data-provider-id="${providerId}"]`,
        `[data-payment-provider-id="${providerId}"]`,
        // Fallback: Liste der Zahlungsoptionen (o_payment_option_card)
        `.o_payment_option_card[data-id="${providerId}"]`,
    ];

    for (const selector of selectors) {
        document.querySelectorAll(selector).forEach((el) => {
            el.style.display = 'none';
            el.setAttribute('aria-hidden', 'true');
            // Verhindert, dass ausgeblendete Radio-Buttons versehentlich
            // submitted werden
            const radio = el.querySelector('input[type="radio"]');
            if (radio) {
                radio.disabled = true;
            }
        });
    }
}

/**
 * Zeigt eine Warnung, wenn alle verfügbaren Provider gesperrt sind.
 *
 * @param {Element} container  #payment_method DOM-Knoten
 */
function showAllBlockedWarning(container) {
    if (container.querySelector('.o_payment_restriction_warning')) return;

    const warning = document.createElement('div');
    warning.className = 'alert alert-warning o_payment_restriction_warning mt-3';
    warning.setAttribute('role', 'alert');
    warning.innerHTML = `
        <strong>Keine Zahlungsart verfügbar</strong><br/>
        Für einen oder mehrere Artikel in Ihrem Warenkorb sind alle
        Zahlungsarten eingeschränkt. Bitte kontaktieren Sie uns für Hilfe.
    `;
    container.prepend(warning);
}

/**
 * Hauptfunktion: fragt den Server ab und versteckt gesperrte Provider.
 */
async function applyPaymentRestrictions() {
    const container = document.querySelector(PAYMENT_PAGE_SELECTOR);
    if (!container) return; // Nicht auf der Payment-Seite → nichts tun

    let blockedIds = [];
    try {
        const result = await rpc('/shop/payment/blocked_providers', {});
        blockedIds = result.blocked_ids || [];
    } catch (error) {
        // Im Fehlerfall lieber alle Provider zeigen als gar keinen
        console.warn('[payment_method_restriction] Konnte gesperrte Provider nicht laden:', error);
        return;
    }

    if (!blockedIds.length) return;

    blockedIds.forEach(hideProvider);

    // Prüfen ob noch sichtbare Provider übrig sind
    const visibleProviders = container.querySelectorAll(
        '[data-provider-id]:not([style*="display: none"]), ' +
        '[data-payment-provider-id]:not([style*="display: none"]), ' +
        '.o_payment_option_card:not([style*="display: none"])'
    );

    if (visibleProviders.length === 0) {
        showAllBlockedWarning(container);
    }
}

// ----------------------------------------------------------------
// Initialisierung: DOMContentLoaded reicht, da wir kein OWL-
// Component wrappen müssen – reines DOM-Manipulation auf einer
// klassischen Seite.
// ----------------------------------------------------------------
document.addEventListener('DOMContentLoaded', () => {
    applyPaymentRestrictions();
});

// Zusätzlich: Falls der Checkout per fetch/AJAX neu gerendert wird
// (z. B. nach Adressänderung), erneut anwenden sobald #payment_method
// im DOM erscheint (MutationObserver als Fallback).
const observer = new MutationObserver(() => {
    if (document.querySelector(PAYMENT_PAGE_SELECTOR)) {
        applyPaymentRestrictions();
        // Einmalig beobachten, danach kurz pausieren um Loops zu vermeiden
        observer.disconnect();
        setTimeout(() => observer.observe(document.body, { childList: true, subtree: true }), 500);
    }
});

observer.observe(document.body, { childList: true, subtree: true });

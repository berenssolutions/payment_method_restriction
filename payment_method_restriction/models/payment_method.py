# -*- coding: utf-8 -*-
import logging

from odoo import api, models
from odoo.http import request

_logger = logging.getLogger(__name__)


class PaymentMethod(models.Model):
    """
    Überschreibt _get_compatible_payment_methods (Odoo 18 API).

    In Odoo 18 zeigt der Checkout-Payment-Widget payment.method-Einträge,
    keine payment.provider direkt. Diese Methode bekommt eine Liste von
    provider_ids (int) übergeben und gibt kompatible payment.method zurück.

    Wir entfernen payment.method-Einträge, deren Provider komplett durch
    Warenkorbartikel gesperrt sind – d.h. alle Provider der Methode sind
    in der Sperrliste des Warenkorbs.

    Originalcode Odoo 18:
      addons/payment/models/payment_method.py – _get_compatible_payment_methods
    """

    _inherit = 'payment.method'

    @api.model
    def _get_compatible_payment_methods(
        self,
        provider_ids,
        partner_id,
        currency_id=None,
        force_tokenization=False,
        is_express_checkout=False,
        report=None,
        **kwargs,
    ):
        """
        Erweitert die Standard-Kompatibilitätsprüfung:
        Nach dem Odoo-Standard-Filter werden payment.method-Einträge entfernt,
        wenn der gesamte zugehörige provider_ids-Schnitt mit der Sperrliste
        identisch ist – d.h. es bleibt kein erlaubter Provider übrig.

        :param list provider_ids: Kompatible Provider-IDs (ints) aus Odoo-Basis
        :param int partner_id: Partner-ID
        :param int currency_id: Währungs-ID
        :param bool force_tokenization: Nur Methoden mit Tokenisierung
        :param bool is_express_checkout: Nur Express-Checkout-Methoden
        :param dict report: Debug-Report-Dict (Odoo 18 neu)
        :return: Gefilterte payment.method Records
        """
        # Erst den Standard-Odoo-18-Filter laufen lassen
        payment_methods = super()._get_compatible_payment_methods(
            provider_ids,
            partner_id,
            currency_id=currency_id,
            force_tokenization=force_tokenization,
            is_express_checkout=is_express_checkout,
            report=report,
            **kwargs,
        )

        # Gesperrte Provider-IDs aus dem aktuellen Warenkorb holen
        blocked_provider_ids = self._get_blocked_provider_ids_from_cart()
        if not blocked_provider_ids:
            return payment_methods

        _logger.debug(
            '[payment_method_restriction] Gesperrte Provider-IDs: %s',
            blocked_provider_ids,
        )

        # provider_ids ist eine Liste von ints (so wie Odoo sie übergibt)
        # Wir bauen die erlaubten Provider: alle aus provider_ids, die NICHT gesperrt sind
        allowed_provider_ids = set(provider_ids) - blocked_provider_ids

        # Eine payment.method fliegt raus, wenn KEINER ihrer Provider in
        # allowed_provider_ids enthalten ist.
        # (Falls sie mehrere Provider hat und mindestens einer erlaubt ist, bleibt sie.)
        def method_has_allowed_provider(pm):
            pm_provider_ids = set(pm.provider_ids.ids)
            # Schnitt mit allowed_provider_ids – muss mindestens 1 enthalten
            return bool(pm_provider_ids & allowed_provider_ids)

        filtered = payment_methods.filtered(method_has_allowed_provider)

        if filtered != payment_methods:
            removed = payment_methods - filtered
            _logger.info(
                '[payment_method_restriction] Ausgeblendete Zahlungsmethoden: %s',
                removed.mapped('name'),
            )

        return filtered

    @api.model
    def _get_blocked_provider_ids_from_cart(self):
        """
        Liest den aktuellen eCommerce-Warenkorb aus dem HTTP-Request-Kontext
        und gibt alle payment.provider-IDs zurück, die von mindestens einem
        Warenkorbartikel gesperrt sind.

        Gibt leere Menge zurück wenn kein aktiver HTTP-Request vorhanden ist
        (Cron, Backend, Unit-Tests).

        :return: set[int] Gesperrte Provider-IDs
        """
        try:
            website = request.website
        except RuntimeError:
            # Kein HTTP-Kontext (z. B. Cron oder Unit-Test)
            return set()

        if not website:
            return set()

        order = website.sale_get_order()
        if not order:
            return set()

        blocked = order.order_line.mapped(
            'product_id.product_tmpl_id.blocked_payment_provider_ids'
        )
        return set(blocked.ids)

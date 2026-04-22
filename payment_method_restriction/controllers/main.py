# -*- coding: utf-8 -*-
import json
import logging

from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale

_logger = logging.getLogger(__name__)


class WebsiteSalePaymentRestriction(WebsiteSale):
    """
    Erweitert den WebsiteSale-Controller, um beim Checkout-Schritt
    Zahlungsanbieter auszublenden, die von Produkten im Warenkorb gesperrt sind.
    """

    @http.route()
    def shop_payment(self, **post):
        """
        Hängt die Liste der gesperrten Provider-IDs an den Rendering-Kontext,
        damit das JS-Snippet sie im DOM gezielt ausblenden kann.
        """
        response = super().shop_payment(**post)

        # Nur bei gerenderten QWeb-Responses weiterarbeiten
        if not hasattr(response, 'qcontext'):
            return response

        blocked_ids = self._get_blocked_provider_ids()
        response.qcontext['blocked_payment_provider_ids'] = blocked_ids

        return response

    # ------------------------------------------------------------------
    # JSON-Endpunkt  –  wird vom JS bei jeder Warenkorbänderung aufgerufen
    # ------------------------------------------------------------------

    @http.route(
        '/shop/payment/blocked_providers',
        type='json',
        auth='public',
        website=True,
        methods=['POST'],
    )
    def get_blocked_providers(self):
        """
        Gibt die IDs aller gesperrten Zahlungsanbieter für den aktuellen
        Warenkorb als JSON zurück.

        Rückgabe:
            {"blocked_ids": [1, 3, 7]}
        """
        blocked_ids = self._get_blocked_provider_ids()
        return {'blocked_ids': blocked_ids}

    # ------------------------------------------------------------------
    # Hilfsmethode
    # ------------------------------------------------------------------

    def _get_blocked_provider_ids(self):
        """
        Ermittelt alle Zahlungsanbieter-IDs, die von mindestens einem Produkt
        im aktuellen Warenkorb gesperrt sind.

        Returns:
            list[int]: Sortierte Liste eindeutiger Provider-IDs.
        """
        order = request.website.sale_get_order()
        if not order:
            return []

        blocked = order.order_line.mapped(
            'product_id.product_tmpl_id.blocked_payment_provider_ids'
        )
        return sorted(blocked.ids)

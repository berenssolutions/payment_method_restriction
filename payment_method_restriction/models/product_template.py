# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ProductTemplate(models.Model):
    """Erweitert product.template um gesperrte Zahlungsarten für den eCommerce-Checkout."""

    _inherit = 'product.template'

    blocked_payment_provider_ids = fields.Many2many(
        comodel_name='payment.provider',
        relation='product_template_blocked_payment_provider_rel',
        column1='product_template_id',
        column2='payment_provider_id',
        string='Gesperrte Zahlungsarten',
        domain=[('state', 'in', ['enabled', 'test'])],
        help=(
            'Zahlungsanbieter, die im eCommerce-Checkout ausgeblendet werden, '
            'sobald sich dieser Artikel im Warenkorb befindet. '
            'Typischer Anwendungsfall: ABO-Artikel nur mit Stripe buchen – PayPal sperren.'
        ),
    )

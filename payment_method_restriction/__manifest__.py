# -*- coding: utf-8 -*-
{
    'name': 'Payment Method Restriction per Product',
    'version': '18.0.1.0.0',
    'category': 'eCommerce',
    'summary': 'Sperrt bestimmte Zahlungsarten im Checkout, wenn ein Artikel mit Einschränkung im Warenkorb liegt',
    'description': """
        Ermöglicht es, auf Artikelebene (Verkauf > E-Commerce-Shop) bestimmte
        Zahlungsanbieter zu sperren. Sobald ein solcher Artikel im Warenkorb ist,
        werden die gesperrten Zahlungsarten im eCommerce-Checkout ausgeblendet.

        Typischer Anwendungsfall: ABO-Artikel können nur per Stripe gebucht werden,
        PayPal muss daher ausgeschlossen werden.
    """,
    'author': 'Lennart Berens, Berens Solutions',
    'website': 'https://berenssolutions.de',
    'maintainer': 'Lennart Berens',
    'license': 'LGPL-3',
    'depends': [
        'website_sale',
        'payment',
        'sale',
    ],
    'data': [
        'views/product_template_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}

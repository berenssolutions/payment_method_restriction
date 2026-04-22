# -*- coding: utf-8 -*-
# Dieses Modul überschreibt _get_compatible_providers auf payment.provider,
# um gesperrte Zahlungsanbieter serverseitig aus dem Checkout zu entfernen.
# Kein JavaScript nötig – der Filter greift bevor die Seite gerendert wird.

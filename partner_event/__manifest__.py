# -*- coding: utf-8 -*-
# Copyright 2014 Tecnativa S.L. - Pedro M. Baeza
# Copyright 2015 Tecnativa S.L. - Javier Iniesta
# Copyright 2016 Tecnativa S.L. - Antonio Espinosa
# Copyright 2016 Tecnativa S.L. - Vicent Cubells
# Copyright 2017 Tecnativa S.L. - David Vidal
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Link partner to events',
    'version': '10.0.2.1.0',
    'category': 'Marketing',
    'author': 'Tecnativa,'
              'Odoo Community Association (OCA)',
    'website': 'https://www.tecnativa.com',
    "license": "AGPL-3",
    'depends': [
        'event',
    ],
    "post_init_hook": "post_init_hook",
    "uninstall_hook": "uninstall_hook",
    'data': [
        'views/res_partner_view.xml',
        'views/event_event_view.xml',
        'views/event_registration_view.xml',
        'wizard/res_partner_register_event_view.xml',
    ],
    'installable': True,
}

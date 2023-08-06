# -*- coding: utf-8 -*-
'''
    Nereid Integration with MailChimp

    :copyright: (c) 2011-2014 by Openlabs Technologies & Consulting (P) Ltd.
    :license: GPLv3, see LICENSE for more details
'''
from trytond.pool import Pool
from site import WebSite
from party import NereidUser


def register():
    Pool.register(
        WebSite,
        NereidUser,
        module='nereid_chimp', type_='model'
    )

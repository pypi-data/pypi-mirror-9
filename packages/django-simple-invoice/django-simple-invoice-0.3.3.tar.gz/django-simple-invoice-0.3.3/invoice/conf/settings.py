# -*- coding: UTF-8 -*-
from os import path
from django.conf import settings


INV_MODULE = getattr(settings, 'INV_MODULE', 'invoice.pdf_example')
INV_LOGO = getattr(settings, 'INV_LOGO',
                   path.join(settings.MEDIA_ROOT, 'static/images/logo.jpg'))
INV_CURRENCY = getattr(settings, 'INV_CURRENCY', u'EUR')
INV_CURRENCY_SYMBOL = getattr(settings, 'INV_CURRENCY_SYMBOL', u'€')
INV_EMAIL_SUBJECT = getattr(settings, 'INV_EMAIL_SUBJECT',
                            u'[%s] Invoice %%(invoice_id)s' % (
                                settings.SITE_NAME))
INV_CLIENT_MODULE = getattr(settings, 'INV_CLIENT_MODULE', 'auth.User')
INV_ID_MODULE = getattr(settings, 'INV_ID_MODULE',
                        'invoice.utils.friendly_id')
INV_PDF_DIR = getattr(settings, 'INV_PDF_DIR',
                      path.join(settings.MEDIA_ROOT, 'invoices/pdf/'))
INV_NAME_MODULE = getattr(settings, 'INV_NAME_MODULE',
                          'invoice.utils.naming')
INV_EXPORT_MODULE = getattr(settings, 'INV_EXPORT_MODULE',
                            'invoice.export_example')

# -*- coding: UTF-8 -*-
'''
    nereid_mailchimp.party

    :copyright: (c) 2010-2014 by Openlabs Technologies & Consulting (P) LTD
    :license: GPLv3, see LICENSE for more details
'''
import json

from wtforms import (
    TextField, validators, HiddenField
)
from flask_wtf import Form
from nereid.globals import current_app
from nereid import request, redirect, url_for, flash, route, jsonify

from trytond.pool import PoolMeta

from .chimp import list_subscribe
from .i18n import _

__all__ = ['NereidUser']
__metaclass__ = PoolMeta


class NewsletterForm(Form):
    "New Newsletter Subscription form"
    name = TextField(_('Name'))
    email = TextField(_('Email ID'), [validators.DataRequired()])
    next = HiddenField('Next')


class NereidUser:
    """Extending user to include newsletter subscription info
    """
    __name__ = 'nereid.user'

    def list_subscribe(self):
        """A helper method which just proxies list_subscribe so that
        this could be accessed by a pool lookup.
        """
        return list_subscribe()

    @classmethod
    @route('/mailing-list/subscribe', methods=['POST'])
    def subscribe_newsletter(cls):
        """This method will allow the user to subscribe to a newsletter
        just by filling up email and name(mandatory for guest user)
        """
        form = NewsletterForm(request.form)
        message = None

        if not form.validate() and request.is_xhr:
            return jsonify(errors=form.errors), 400

        result = json.loads(list_subscribe().data)
        if not result['success']:
            current_app.logger.error(result)
            if "already subscribed" in result['message']:
                message = _(result['message'])
                if request.is_xhr:
                    return jsonify(message=unicode(message)), 409
            else:
                message = _(
                    'We could not subscribe you into the newsletter.'
                    ' Try again later'
                )
            if request.is_xhr:
                return jsonify(message=unicode(message)), 501
        else:
            message = _(
                'You have been successfully subscribed to newsletters.'
            )

        if request.is_xhr:
            return jsonify(message=message and unicode(message))

        flash(message or "Please fill form properly")
        return redirect(
            request.values.get('next', url_for('nereid.website.home'))
        )

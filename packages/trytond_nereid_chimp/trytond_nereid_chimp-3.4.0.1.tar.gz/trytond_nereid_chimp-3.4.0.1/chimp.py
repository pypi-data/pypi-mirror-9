# -*- coding: utf-8 -*-
"""
    chimp

    Implements the view function for subscription

    :copyright: (c) 2011-2014 by Openlabs Technologies & Consulting (P) Limited
    :license: GPLv3, see LICENSE for more details.
"""
from nereid import request, jsonify, current_app

from chimpy import Connection
from chimpy.chimpy import ChimpyException


def list_subscribe():
    """Subscribes an user to the mailing list

    Inspected arguments in a POST request

    If first_name and last_name is given it is used
    Else name is split into two to be used

    Then the form is inspected for `mailing_list`. If provided the value
    is used as ID for the subscription. If not the default list is used for
    subscription. you could put in this value as a hidden field in the form

    Always returns a JSON response:
    {
        'success': True or False,
        'message': A message (Not recommended to be displayed to user)
    }
    """
    if not request.nereid_website.mailchimp_api_key:
        current_app.logger.error("nereid-mailchimp No API key")
        return jsonify(
            success=False,
            message="No API Configured"
        )

    if request.method == 'POST':
        # Mailchimp requires first name and last name, but nereid probably
        # took only the name field. Check for the keys to decide what to pick
        email = request.values['email']

        merge_vars = {}
        keys = request.values.keys()

        if 'first_name' in keys and 'last_name' in keys:
            merge_vars['FNAME'], merge_vars['LNAME'] = (
                request.values['first_name'], request.values['last_name'])
        elif 'name' in keys:
            try:
                merge_vars['FNAME'], merge_vars['LNAME'] = request.values[
                    'name'].split(' ', 1)
            except ValueError:
                merge_vars['FNAME'] = merge_vars['LNAME'] = \
                    request.values['name']
        else:
            merge_vars.update({'FIRST': '', 'LAST': ''})

        chimpy_connection = Connection(
            request.nereid_website.mailchimp_api_key
        )

        mailing_list = request.values['mailing_list'] \
            if 'mailing_list' in keys else None
        if mailing_list is None:
            # If no mailing list was there in the form then use the default one
            lists = chimpy_connection.lists()
            mailing_list_name = request.nereid_website.mailchimp_default_list
            for each_list in lists:
                if each_list['name'] == mailing_list_name:
                    mailing_list = each_list['id']
                    break
            else:
                return jsonify(
                    success=False,
                    message="No mailing list specified, default one not found"
                )
        #  Call Subscribe
        merge_vars['OPTIN_IP'] = request.remote_addr
        try:
            chimpy_connection.list_subscribe(mailing_list, email, merge_vars)
        except ChimpyException, exc:
            return jsonify(success=False, message=exc[0])
        return jsonify(success=True, message="Successfuly subscribed user!")

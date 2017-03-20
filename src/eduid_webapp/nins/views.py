# -*- coding: utf-8 -*-
#
# Copyright (c) 2016 NORDUnet A/S
# All rights reserved.
#
#   Redistribution and use in source and binary forms, with or
#   without modification, are permitted provided that the following
#   conditions are met:
#
#     1. Redistributions of source code must retain the above copyright
#        notice, this list of conditions and the following disclaimer.
#     2. Redistributions in binary form must reproduce the above
#        copyright notice, this list of conditions and the following
#        disclaimer in the documentation and/or other materials provided
#        with the distribution.
#     3. Neither the name of the NORDUnet nor the names of its
#        contributors may be used to endorse or promote products derived
#        from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#
from __future__ import absolute_import

from flask import Blueprint, session, abort, current_app

from eduid_common.api.decorators import require_dashboard_user, MarshalWith, UnmarshalWith
from eduid_webapp.nins.schemas import NinsSchema, CodeSchema

nins_views = Blueprint('nins', __name__, url_prefix='', template_folder='templates')


@nins_views.route('/all', methods=['GET'])
@MarshalWith(NinsSchema)
@require_dashboard_user
def get_nins(user, csrf_token):
    '''
    View to get nin for the logged user

    If the user has verified or is in the process of verify returns his nin
    '''
    if session.get_csrf_token() != csrf_token:
        abort(400)

    current_app.logger.debug('Trying to get nin for user {!r}'.format(user))

    # TODO: logic
    code = '199002020202'
    current_app.logger.info('the user {!r} has nin {!r}'.format(user, code))
    current_app.statsd.count(name='nins_get_nin', value=1)

    return code


@nins_views.route('/verify_letter', methods=['POST'])
@UnmarshalWith(NinsSchema)
@MarshalWith(NinsSchema)
@require_dashboard_user
def verify_letter(user, code, csrf_token):
    '''
    View to verify identity using a physical letter

    Return 200 if nin is valid
    '''
    if session.get_csrf_token() != csrf_token:
        abort(400)

    current_app.logger.debug('Trying to verify nin {!r} '
                             'for user {!r} using physical letter'.format(code, user))

    # TODO: logic
    current_app.logger.info('sending letter to nin {!r} '
                            'for user {!r}'.format(code, user))
    current_app.statsd.count(name='nins_sended_letter', value=1)

    return 200


@nins_views.route('/verify_phone', methods=['POST'])
@UnmarshalWith(NinsSchema)
@MarshalWith(NinsSchema)
@require_dashboard_user
def verify_phone(user, code, csrf_token):
    '''
    View to verify identity using a mobile phone

    Return 200 if nin is valid
    '''
    if session.get_csrf_token() != csrf_token:
        abort(400)

    current_app.logger.debug('Trying to verify nin {!r} '
                             'for user {!r} using mobile'.format(code, user))

    # TODO: logic
    number = '+34670123123'
    current_app.logger.info('sending sms to nin {!r} '
                            'for user {!r} with number {!r}'.format(code, user, number))
    current_app.statsd.count(name='nins_sended_sms', value=1)

    return 200


@nins_views.route('/verify_letter', methods=['POST'])
@UnmarshalWith(CodeSchema)
@MarshalWith(CodeSchema)
@require_dashboard_user
def confirm_letter(user, code, csrf_token):
    '''
    View to confirm identity using a physical letter

    Return 200 if is verified
    '''
    if session.get_csrf_token() != csrf_token:
        abort(400)

    current_app.logger.debug('Trying to confirm nin {!r} '
                             'for user {!r} using physical letter'.format(code, user))

    # TODO: logic
    current_app.logger.info('confirmed nin {!r} '
                            'for user {!r}'.format(code, user))
    current_app.statsd.count(name='nins_confirmed_letter', value=1)

    return 200


@nins_views.route('/verify_phone', methods=['POST'])
@UnmarshalWith(CodeSchema)
@MarshalWith(CodeSchema)
@require_dashboard_user
def confirm_phone(user, code, csrf_token):
    '''
    View to confirm identity using a mobile phone

    Return 200 if is verified
    '''
    if session.get_csrf_token() != csrf_token:
        abort(400)

    current_app.logger.debug('Trying to confirm nin {!r} '
                             'for user {!r} using mobile'.format(code, user))

    # TODO: logic
    number = '+34670123123'
    current_app.logger.info('confirmed sms {!r} '
                            'for user {!r} with number {!r}'.format(code, user, number))
    current_app.statsd.count(name='nins_confirmed_mobile', value=1)

    return 200

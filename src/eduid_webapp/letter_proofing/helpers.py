# -*- coding: utf-8 -*-

from __future__ import absolute_import

from flask import current_app
from datetime import datetime, timedelta

from eduid_userdb.proofing import LetterProofingState
from eduid_common.api.utils import get_short_hash
from eduid_webapp.letter_proofing import pdf

__author__ = 'lundberg'


def check_state(state):
    """
    :param state:  Users proofing state
    :type state:  LetterProofingState
    :return: payload
    :rtype: dict
    """
    current_app.logger.info('Checking state for user with eppn {!s}'.format(state.eppn))
    if state.proofing_letter.is_sent:
        current_app.logger.info('Letter is sent for user with eppn {!s}'.format(state.eppn))
        # Check how long ago the letter was sent
        sent_dt = state.proofing_letter.sent_ts
        minutes_until_midnight = (24 - sent_dt.hour) * 60  # Give the user until midnight the day the code expires
        now = datetime.now(sent_dt.tzinfo)  # Use tz_info from timezone aware mongodb datetime
        max_wait = timedelta(hours=current_app.config['LETTER_WAIT_TIME_HOURS'], minutes=minutes_until_midnight)

        time_since_sent = now - sent_dt
        if time_since_sent < max_wait:
            current_app.logger.info('User with eppn {!s} has to wait for letter to arrive.'.format(state.eppn))
            current_app.logger.info('Code expires: {!s}'.format(sent_dt + max_wait))
            # The user has to wait for the letter to arrive
            return {
                'letter_sent': sent_dt,
                'letter_expires': sent_dt + max_wait,
            }
        else:
            # If the letter haven't reached the user within the allotted time
            # remove the previous proofing object and restart the proofing flow
            current_app.logger.info('Letter expired for user with eppn {!s}.'.format(state.eppn))
            current_app.proofing_statedb.remove_document({'eduPersonPrincipalName': state.eppn})
            current_app.logger.info('Removed {!s}'.format(state))
            return {
                'letter_expired': True,
            }
    current_app.logger.info('Unfinished state for user with eppn {!s}'.format(state.eppn))
    return {}


def create_proofing_state(eppn, nin):
    proofing_state = LetterProofingState({
        'eduPersonPrincipalName': eppn,
        'nin': {
            'number': nin,
            'created_by': 'eduid-idproofing-letter',
            'created_ts': True,
            'verified': False,
            'verification_code': get_short_hash()
        }
    })
    return proofing_state


def get_address(user, proofing_state):
    """
    :param user: User object
    :param proofing_state: Users proofing state

    :type user: eduid_userdb.proofing.ProofingUser
    :type proofing_state: eduid_userdb.proofing.LetterProofingState

    :return: Users offcial postal address
    :rtype: OrderedDict|None
    """
    current_app.logger.info('Getting address for user {!r}'.format(user))
    current_app.logger.debug('NIN: {!s}'.format(proofing_state.nin.number))
    # Lookup official address via Navet
    address = current_app.msg_relay.get_postal_address(proofing_state.nin.number)
    current_app.logger.debug('Official address: {!r}'.format(address))
    return address


def send_letter(user, proofing_state):
    """
    :param user: User object
    :param proofing_state: Users proofing state

    :type user: eduid_userdb.proofing.ProofingUser
    :type proofing_state: eduid_userdb.proofing.LetterProofingState

    :return: Transaction id
    :rtype: str|unicode
    """
    # Create the letter as a PDF-document and send it to our letter sender service
    if current_app.config.get("EKOPOST_DEBUG_PDF", None):
        pdf.create_pdf(proofing_state.proofing_letter.address,
                       proofing_state.nin.verification_code,
                       proofing_state.nin.created_ts,
                       user.mail_addresses.primary.email)
        campaign_id = 'debug mode transaction id'
    else:
        pdf_letter = pdf.create_pdf(proofing_state.proofing_letter.address,
                                    proofing_state.nin.verification_code,
                                    proofing_state.nin.created_ts,
                                    user.mail_addresses.primary.email)

        campaign_id = current_app.ekopost.send(user.eppn, pdf_letter)
    return campaign_id

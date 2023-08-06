# -*- coding: utf-8 -*-
#
# Copyright (C) 2014, All Rights Reserved, PokitDok, Inc.
# https://www.pokitdok.com
#
# Please see the License.txt file for more information.
# All other rights reserved.
#

from __future__ import absolute_import
import json
import os
import pokitdok
import requests
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import BackendApplicationClient


class PokitDokClient(object):
    """
        PokitDok Platform API Client
        This class provides a wrapper around requests and requests-oauth
        to handle common API operations
    """
    def __init__(self, client_id, client_secret, base="https://platform.pokitdok.com", version="v4",
                 redirect_uri=None, scope=None, auto_refresh=False, token_refresh_callback=None, code=None):
        """
            Initialize a new PokitDok API Client

            :param client_id: The client id for your PokitDok Platform Application
            :param client_secret: The client secret for your PokitDok Platform Application
            :param base: The base URL to use for API requests.  Defaults to https://platform.pokitdok.com
            :param version: The API version that should be used for requests.  Defaults to the latest version.
            :param redirect_uri: The Redirect URI set for the PokitDok Platform Application.
                                 This value is managed at https://platform.pokitdok.com in the App Settings
            :param scope: a list of scope names that should be used when requesting authorization
            :param auto_refresh: Boolean to indicate whether or not access tokens should be automatically
                                 refreshed when they expire.
            :param token_refresh_callback: a function that should be called when token information is refreshed.
            :param code: code value received from an authorization code grant
        """
        self.base_headers = {
            'User-Agent': 'python-pokitdok/{0} {1}'.format(pokitdok.__version__, requests.utils.default_user_agent())
        }
        self.json_headers = {
            'Content-type': 'application/json',
        }
        self.json_headers.update(self.base_headers)
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.scope = scope
        self.code = code
        self.auto_refresh = auto_refresh
        self.token_refresh_callback = token_refresh_callback
        self.token = {}
        self.url_base = "{0}/api/{1}".format(base, version)
        self.token_url = "{0}/oauth2/token".format(base)
        self.authorize_url = "{0}/oauth2/authorize".format(base)
        self.api_client = None
        self.fetch_access_token(code=self.code)

    def initialize_auth_api_client(self, refresh_url):
        self.api_client = OAuth2Session(self.client_id, redirect_uri=self.redirect_uri, scope=self.scope,
                                        auto_refresh_url=refresh_url, token_updater=self.token_refresh_callback,
                                        auto_refresh_kwargs={
                                            'client_id': self.client_id,
                                            'client_secret': self.client_secret})

    def authorization_url(self):
        """
            Construct OAuth2 Authorization Grant URL
            :return: (authorization url, state value) tuple
        """
        refresh_url = self.token_url if self.auto_refresh else None
        self.initialize_auth_api_client(refresh_url)
        return self.api_client.authorization_url(self.authorize_url)

    def fetch_access_token(self, code=None):
        """
            Retrieves an OAuth2 access token.  If `code` is not specified, the client_credentials
            grant type will be used based on the client_id and client_secret.  If `code` is not None,
            an authorization_code grant type will be used.
            :param code: optional code value obtained via an authorization grant
            :return: the client application's token information as a dictionary
        """
        refresh_url = self.token_url if self.auto_refresh else None
        if code is None:

            self.api_client = OAuth2Session(self.client_id, client=BackendApplicationClient(self.client_id),
                                            auto_refresh_url=refresh_url, token_updater=self.token_refresh_callback,
                                            auto_refresh_kwargs={
                                                'client_id': self.client_id,
                                                'client_secret': self.client_secret})
            self.token = self.api_client.fetch_token(self.token_url, client_id=self.client_id,
                                                     client_secret=self.client_secret)
        else:
            self.code = code
            self.initialize_auth_api_client(refresh_url)
            self.token = self.api_client.fetch_token(self.token_url, code=code, client_id=self.client_id,
                                                     client_secret=self.client_secret, scope=self.scope)
        return self.token

    def activities(self, activity_id=None, **kwargs):
        """
            Fetch platform activity information

            :param activity_id: the id of a specific platform activity that should be retrieved.
                                If omitted, an index listing of activities is returned.  If included
                                other keyword arguments are ignored.

            Keyword arguments that may be used to refine an activity search:

            :param parent_id: The parent activity id of the activities.  This is used to track
                              child activities that are the result of a batch operation.

        """
        activities_url = "{0}/activities/{1}".format(self.url_base, activity_id if activity_id else '')
        request_args = {}
        if activity_id is None:
            request_args.update(kwargs)

        return self.api_client.get(activities_url, params=request_args, headers=self.base_headers).json()

    def cash_prices(self, **kwargs):
        """
            Fetch cash price information
        """
        cash_prices_url = "{0}/prices/cash".format(self.url_base)
        return self.api_client.get(cash_prices_url, params=kwargs, headers=self.base_headers).json()

    def claims(self, claims_request):
        """
            Submit a claims request

            :param claims_request: dictionary representing a claims request
        """
        claims_url = "{0}/claims/".format(self.url_base)
        return self.api_client.post(claims_url, data=json.dumps(claims_request), headers=self.json_headers).json()

    def claims_status(self, claims_status_request):
        """
            Submit a claims status request

            :param claims_status_request: dictionary representing a claims status request
        """
        claims_status_url = "{0}/claims/status".format(self.url_base)
        return self.api_client.post(claims_status_url, data=json.dumps(claims_status_request),
                                    headers=self.json_headers).json()

    def mpc(self, code=None, **kwargs):
        """
            Access clinical and consumer friendly information related to medical procedures

            :param code: A specific procedure code that should be used to retrieve information

            Keyword arguments that may be used to refine a medical procedure search:

            :param name: Search medical procedure information by consumer friendly name
            :param description: A partial or full description to be used to locate medical procedure information
        """

        mpc_url = "{0}/mpc/{1}".format(self.url_base, code if code else '')
        request_args = {}
        if code is None:
            request_args.update(kwargs)

        return self.api_client.get(mpc_url, params=request_args, headers=self.base_headers).json()

    def eligibility(self, eligibility_request):
        """
            Submit an eligibility request

            :param eligibility_request: dictionary representing an eligibility request
        """
        eligibility_url = "{0}/eligibility/".format(self.url_base)
        return self.api_client.post(eligibility_url, data=json.dumps(eligibility_request),
                                    headers=self.json_headers).json()

    def enrollment(self, enrollment_request):
        """
            Submit a benefits enrollment/maintenance request

            :param enrollment_request: dictionary representing an enrollment request
        """
        enrollment_url = "{0}/enrollment/".format(self.url_base)
        return self.api_client.post(enrollment_url, data=json.dumps(enrollment_request),
                                    headers=self.json_headers).json()

    def files(self, trading_partner_id, x12_file):
        """
            Submit a raw X12 file to the platform for processing

            :param trading_partner_id: the trading partner that should receive the X12 file information
            :param x12_file: the path to a X12 file to be submitted to the platform for processing
        """
        files_url = "{0}/files/".format(self.url_base)
        return self.api_client.post(files_url,
                                    headers=self.base_headers,
                                    data={'trading_partner_id': trading_partner_id},
                                    files={'file': (os.path.split(x12_file)[-1], open(x12_file, 'rb'),
                                                    'application/EDI-X12')}).json()

    def insurance_prices(self, **kwargs):
        """
            Fetch insurance price information
        """
        insurance_prices_url = "{0}/prices/insurance".format(self.url_base)
        return self.api_client.get(insurance_prices_url, params=kwargs, headers=self.base_headers).json()

    def payers(self, **kwargs):
        """
            Fetch payer information for supported trading partners

        """
        request_args = {}
        request_args.update(kwargs)

        payers_url = "{0}/payers/".format(self.url_base)
        return self.api_client.get(payers_url, params=request_args, headers=self.base_headers).json()

    def plans(self, **kwargs):
        """
            Fetch insurance plans information
        """
        insurance_plans_url = "{0}/plans/".format(self.url_base)
        return self.api_client.get(insurance_plans_url, params=kwargs, headers=self.base_headers).json()

    def providers(self, npi=None, **kwargs):
        """
            Search health care providers in the PokitDok directory

            :param npi: The National Provider Identifier for an Individual Provider or Organization
                        When a NPI value is specified, no other parameters will be considered.

            Keyword arguments that may be used to refine a providers search:

            :param zipcode: A zip code that should be searched in/around for providers
            :param radius: A value representing the search distance from a geographic center point
                           May be expressed in miles like: 10mi
            :param first_name: The first name of a provider to include in the search criteria
            :param last_name: The last name of a provider to include in the search criteria
            :param limit: The number of provider results that should be included in search results

        """

        providers_url = "{0}/providers/{1}".format(self.url_base, npi if npi else '')
        request_args = {}
        if npi is None:
            request_args.update(kwargs)

        return self.api_client.get(providers_url, params=request_args, headers=self.base_headers).json()

    def trading_partners(self, trading_partner_id=None):
        """
            Search trading partners in the PokitDok Platform

            :param trading_partner_id: the ID used by PokitDok to uniquely identify a trading partner

            :returns a dictionary containing the specified trading partner or, if called with no arguments, a list of
                     available trading partners
        """
        trading_partners_url = "{0}/tradingpartners/{1}".format(self.url_base,
                                                                trading_partner_id if trading_partner_id else '')
        return self.api_client.get(trading_partners_url, headers=self.base_headers).json()

    def referrals(self, referral_request):
        """
            Submit a referral request
            :param referral_request: dictionary representing a referral request
        """
        referrals_url = "{0}/referrals/".format(self.url_base)
        return self.api_client.post(referrals_url, data=json.dumps(referral_request),
                                    headers=self.json_headers).json()

    def authorizations(self, authorizations_request):
        """
            Submit an authorization request
            :param authorizations_request: dictionary representing an authorization request
        """
        authorizations_url = "{0}/authorizations/".format(self.url_base)
        return self.api_client.post(authorizations_url, data=json.dumps(authorizations_request),
                                    headers=self.json_headers).json()

    def schedulers(self, scheduler_uuid=None):
        """
            Get information about supported scheduling systems or fetch data about a specific scheduling system
            :param scheduler_uuid: The uuid of a specific scheduling system.
        """
        schedulers_url = "{0}/schedule/schedulers/{1}".format(self.url_base, scheduler_uuid if scheduler_uuid else '')
        return self.api_client.get(schedulers_url, headers=self.base_headers).json()

    def appointment_types(self, appointment_type_uuid=None):
        """
            Get information about appointment types or fetch data about a specific appointment type
            :param appointment_type_uuid: The uuid of a specific appointment type.
        """
        appointment_types_url = "{0}/schedule/appointmenttypes/{1}".format(self.url_base,
                                                                           appointment_type_uuid if appointment_type_uuid else '')
        return self.api_client.get(appointment_types_url, headers=self.base_headers).json()

    def schedule_slots(self, slots_request):
        """
            Submit an open slot for a provider's schedule
            :param slots_request: dictionary representing a slots request
        """
        slots_url = "{0}/schedule/slots/".format(self.url_base)
        return self.api_client.post(slots_url, data=json.dumps(slots_request),
                                    headers=self.json_headers).json()

    def appointments(self, appointment_uuid=None, **kwargs):
        """
            Query for open appointment slots or retrieve information for a specific appointment
            :param appointment_uuid: The uuid of a specific appointment.
        """
        request_args = {}
        appointments_url = "{0}/schedule/appointments/{1}".format(self.url_base,
                                                                  appointment_uuid if appointment_uuid else '')
        if appointment_uuid is None:
            request_args.update(kwargs)
        return self.api_client.get(appointments_url, params=request_args, headers=self.base_headers).json()

    def book_appointment(self, appointment_uuid, appointment_request):
        """
            Book an appointment
            :param appointment_uuid: The uuid of a specific appointment to be booked.
            :param appointment_request: the appointment request data
        """
        appointments_url = "{0}/schedule/appointments/{1}".format(self.url_base, appointment_uuid)
        return self.api_client.put(appointments_url, data=json.dumps(appointment_request),
                                   headers=self.json_headers).json()

    update_appointment = book_appointment

    def cancel_appointment(self, appointment_uuid):
        """
            Cancel an appointment
            :param appointment_uuid: The uuid of a specific appointment.
        """
        appointments_url = "{0}/schedule/appointments/{1}".format(self.url_base, appointment_uuid)
        return self.api_client.delete(appointments_url, headers=self.base_headers).json()


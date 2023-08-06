|build| |version| |wheel| |python3|

PokitDok Platform API Client for Python
=======================================

Installation
------------

Install from PyPI_ using pip_

.. code-block:: bash

    $ pip install pokitdok


Resources
---------

Report issues_ on GitHub


Quick start
-----------

.. code-block:: python

    import pokitdok

    pd = pokitdok.api.connect('<your client id>', '<your client secret>')

    #retrieve cash price information by zip and CPT code
    pd.cash_prices(zip_code='32218', cpt_code='87799')

    #retrieve insurance price information by zip and CPT code
    pd.insurance_prices(zip_code='32218', cpt_code='87799')

    #retrieve provider information by NPI
    pd.providers(npi='1467560003')

    #search providers by name (individuals)
    pd.providers(first_name='Jerome', last_name='Aya-Ay')

    #search providers by name (organizations)
    pd.providers(organization_name='Qliance')

    #search providers by location and/or specialty
    pd.providers(zipcode='29307', radius='10mi')
    pd.providers(zipcode='29307', radius='10mi', specialty='RHEUMATOLOGY')

    #submit a v4 eligibility request
    pd.eligibility({
        "member": {
            "birth_date": "1970-01-01",
            "first_name": "Jane",
            "last_name": "Doe",
            "id": "W000000000"
        },
        "provider": {
            "first_name": "JEROME",
            "last_name": "AYA-AY",
            "npi": "1467560003"
        },
        "service_types": ["health_benefit_plan_coverage"],
        "trading_partner_id": "MOCKPAYER"
    })

    #submit a v4 claims request
    pd.claims({
        "transaction_code": "chargeable",
        "trading_partner_id": "MOCKPAYER",
        "billing_provider": {
            "taxonomy_code": "207Q00000X",
            "first_name": "Jerome",
            "last_name": "Aya-Ay",
            "npi": "1467560003",
            "address": {
                "address_lines": [
                    "8311 WARREN H ABERNATHY HWY"
                ],
                "city": "SPARTANBURG",
                "state": "SC",
                "zipcode": "29301"
            },
            "tax_id": "123456789"
        },
        "subscriber": {
            "first_name": "Jane",
            "last_name": "Doe",
            "member_id": "W000000000",
            "address": {
                "address_lines": ["123 N MAIN ST"],
                "city": "SPARTANBURG",
                "state": "SC",
                "zipcode": "29301"
            },
            "birth_date": "1970-01-01",
            "gender": "female"
        },
        "claim": {
            "total_charge_amount": 60.0,
            "service_lines": [
                {
                    "procedure_code": "99213",
                    "charge_amount": 60.0,
                    "unit_count": 1.0,
                    "diagnosis_codes": [
                        "487.1"
                    ],
                    "service_date": "2014-06-01"
                }
            ]
        }
    })

    #Check the status of a claim
    pd.claims_status({
        "patient": {
            "birth_date": "1970-01-01",
            "first_name": "JANE",
            "last_name": "DOE",
            "id": "1234567890"
        },
        "provider": {
            "first_name": "Jerome",
            "last_name": "Aya-Ay",
            "npi": "1467560003",
        },
        "service_date": "2014-01-01",
        "trading_partner_id": "MOCKPAYER"
    })

    #Submit a referral request
    pd.referrals({
        "event": {
            "category": "specialty_care_review",
            "certification_type": "initial",
            "delivery": {
                "quantity": 1,
                "quantity_qualifier": "visits"
            },
            "diagnoses": [
                {
                    "code": "384.20",
                    "date": "2014-09-30"
                }
            ],
            "place_of_service": "office",
            "provider": {
                "first_name": "JOHN",
                "npi": "1154387751",
                "last_name": "FOSTER",
                "phone": "8645822900"
            },
            "type": "consultation"
        },
        "patient": {
            "birth_date": "1970-01-01",
            "first_name": "JANE",
            "last_name": "DOE",
            "id": "1234567890"
        },
        "provider": {
            "first_name": "CHRISTINA",
            "last_name": "BERTOLAMI",
            "npi": "1619131232"
        },
        "trading_partner_id": "MOCKPAYER"
    })

    #Submit an authorization request
    pd.authorizations({
        "event": {
            "category": "health_services_review",
            "certification_type": "initial",
            "delivery": {
                "quantity": 1,
                "quantity_qualifier": "visits"
            },
            "diagnoses": [
                {
                    "code": "789.00",
                    "date": "2014-10-01"
                }
            ],
            "place_of_service": "office",
            "provider": {
                "organization_name": "KELLY ULTRASOUND CENTER, LLC",
                "npi": "1760779011",
                "phone": "8642341234"
            },
            "services": [
                {
                    "cpt_code": "76700",
                    "measurement": "unit",
                    "quantity": 1
                }
            ],
            "type": "diagnostic_imaging"
        },
        "patient": {
            "birth_date": "1970-01-01",
            "first_name": "JANE",
            "last_name": "DOE",
            "id": "1234567890"
        },
        "provider": {
            "first_name": "JEROME",
            "npi": "1467560003",
            "last_name": "AYA-AY"
        },
        "trading_partner_id": "MOCKPAYER"
    })

    #Submit X12 files directly for processing on the platform
    pd.files('MOCKPAYER', '/x12_files/eligibility_requests_batch_20.270')

    #Check on pending platform activities

    #check on a specific activity
    pd.activities(activity_id='5362b5a064da150ef6f2526c')

    #check on a batch of activities
    pd.activities(parent_id='537cd4b240b35755f5128d5c')

    #retrieve an index of activities
    pd.activities()

    #retrieve an index of trading partners
    pd.trading_partners()

    #retrieve a specific trading_partner
    pd.trading_partners("MOCKPAYER")

    #retrieve insurance plan information.  For example, EPO plans in Texas.
    pd.plans(state='TX', plan_type='EPO')



See the documentation_ for detailed information on all of the PokitDok Platform APIs.
The Quick Start Guide is also available as an IPython_ notebook_.


Authentication and Authorization
--------------------------------

Access to PokitDok APIs is controlled via OAuth2.  Most APIs are accessible with an
access token acquired via a client credentials grant type since scope and account context
are not required for their use.  If you're just interested in using APIs that don't
require a specific scope and account context, you simply supply your app credentials
and you're ready to go:


.. code-block:: python

    import pokitdok

    pd = pokitdok.api.connect('<your client id>', '<your client secret>')



if you'd like your access token to automatically refresh, you can connect like this:

.. code-block:: python

    pd = pokitdok.api.connect('<your client id>', '<your client secret>', auto_refresh=True)


That instructs the Python client to use your refresh token to request a new access token
when the access token expires after 1 hour.

For APIs that require a specific scope/account context in order to execute,  you'll need to request
authorization from a user prior to requesting an access token.

.. code-block:: python

    def new_token_handler(token):
        print('new token received: {0}'.format(token))
        # persist token information for later use

    pd = pokitdok.api.connect('<your client id>', '<your client secret>', redirect_uri='https://yourapplication.com/redirect_uri', scope=['user_schedule'], auto_refresh=True, token_refresh_callback=new_token_handler)

    authorization_url, state = pd.authorization_url()
    #redirect the user to authorization_url


You may set your application's redirect uri value via the PokitDok Platform Dashboard (https://platform.pokitdok.com)
The redirect uri specified for authorization must match your registered redirect uri exactly.

After a user has authorized the requested scope, the PokitDok Platform will redirect back to your application's
Redirect URI along with a code and the state value that was included in the authorization url.
If the state matches the original value, you may use the code to fetch an access token:

.. code-block:: python

    pd.fetch_access_token(code='<code value received via redirect>')


Your application may now access scope protected APIs on behalf of the user that authorized the request.
Be sure to retain the token information to ensure you can easily request an access token when you need it
without going back through the authorization code grant redirect flow.   If you don't retain the token
information or the user revokes your authorization, you'll need to go back through the authorization process
to get a new access token for scope protected APIs.

Supported Python Versions
-------------------------

This library aims to support and is tested against these Python versions:

* 2.6.9
* 2.7.6
* 3.4.0
* PyPy

You may have luck with other interpreters - let us know how it goes.

License
-------

Copyright (c) 2014 PokitDok, Inc.  See LICENSE_ for details.

.. _documentation: https://platform.pokitdok.com
.. _issues: https://github.com/pokitdok/pokitdok-python/issues
.. _PyPI: https://pypi.python.org/pypi
.. _pip: https://pypi.python.org/pypi/pip
.. _LICENSE: LICENSE.txt
.. _IPython: http://ipython.org/
.. _notebook: notebooks/PlatformQuickStartDemo.ipynb

.. |version| image:: https://badge.fury.io/py/pokitdok.svg
    :target: https://pypi.python.org/pypi/pokitdok/

.. |build| image:: https://api.travis-ci.org/pokitdok/pokitdok-python.svg
    :target: https://travis-ci.org/pokitdok/pokitdok-python

.. |wheel| image:: https://pypip.in/wheel/pokitdok/badge.png
    :target: https://pypi.python.org/pypi/pokitdok/

.. |python3| image:: https://caniusepython3.com/project/pokitdok.svg
    :target: https://caniusepython3.com/project/pokitdok

Magic Kard Market Python SDK
============================

Setup
-----

To install:

    pip install mkm-sdk

For the SDK to work properly you have to set four environment variables:
* MKM_APP_TOKEN
* MKM_APP_SECRET
* MKM_ACCESS_TOKEN
* MKM_ACCESS_TOKEN_SECRET

Requirements
------------

* Python 2.7/3.4
* Requests
* Requests_OAuthlib

Usage
-----

To receive a response you have to make a request like this:

    mkm.account_management.account()

    mkm.market_place.user(user='SampleUser')
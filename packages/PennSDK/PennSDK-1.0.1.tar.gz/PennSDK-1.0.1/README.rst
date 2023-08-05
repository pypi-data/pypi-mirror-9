=======================================
PennSDK: Wrapper for Multiple Penn APIs
=======================================

.. image:: https://badge.fury.io/py/PennSDK.png
    :target: http://badge.fury.io/py/PennSDK

.. image:: https://pypip.in/d/PennSDK/badge.png
        :target: https://crate.io/packages/PennSDK/

.. image:: https://travis-ci.org/pennlabs/penn-sdk-python.svg
    :target: https://travis-ci.org/pennlabs/penn-sdk-python

Penn SDK is the Python library for writing code that interfaces with University of Pennsylvania
data. It consists of wrappers for the Registrar, Dining, and
Directory API's


Getting an API key
------------------

To use these libraries, you must first obtain an API token and password,
which can be done here_. There are separate API tokens for each.


Documentation
-------------

The full API documentation can be found at
https://esb.isc-seo.upenn.edu/8091/documentation/.

Documentation for the wrapper can be found at http://penn-sdk.readthedocs.org/

Running Tests
-------------

Once you have an API token and password, you can run the tests by creating a
``tests/credentials.py`` file with them as constants. Depending on what you
want to test, include the following variables. They will be retrieved from your
environment variables by default.

.. code-block:: python

    REG_USERNAME = 'MY_REGISTAR_USERNAME'
    REG_PASSWORD = 'MY_REGISTAR_PASSWORD'

    DIN_USERNAME = 'MY_DINING_USERNAME'
    DIN_PASSWORD = 'MY_DINING_PASSWORD'

    DIR_USERNAME = 'MY_DIRECTORY_USERNAME'
    DIR_PASSWORD = 'MY_DIRECTORY_PASSWORD'

    TRANSIT_USERNAME = 'MY_DIRECTORY_USERNAME'
    TRANSIT_PASSWORD = 'MY_DIRECTORY_PASSWORD'

Then run ``make test`` to run all tests in your shell.

Contributing & Bug Reporting
----------------------------

If you find a bug, please submit it through the `GitHub issues page`_.

Pull requests are welcome!

.. _`GitHub issues page`: https://github.com/pennlabs/penn-sdk-python/issues
.. _`here`: https://secure.www.upenn.edu/computing/da/webloginportal/eforms/index.html?content=kew/EDocLite?edlName=openDataRequestForm&userAction=initiate

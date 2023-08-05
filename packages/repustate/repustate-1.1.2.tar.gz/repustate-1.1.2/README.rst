Python Client for Repustate API
===============================

This is a Python client to the Repustate API. You must first get an API
key from `Repustate.com`_

Here’s a simple example of how to use the Python client:

::

    >>> import repustate
    >>> client = repustate.Client(api_key='YOUR_API_KEY')
    >>> client.score(text='I want the sentiment for this lovely text')
    {"status":"OK", "score":0.3782}

You can use the Repustate API to perform text analytics in multiple
languages including:

-  Arabic
-  Chinese
-  English
-  French
-  German
-  Italian
-  Russian
-  Spanish
-  More coming soon …

.. _Repustate.com: https://www.repustate.com

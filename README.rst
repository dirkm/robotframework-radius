****************************************
RadiusLibrary
****************************************

.. image:: https://travis-ci.org/deviousops/robotframework-radius.svg?branch=master
    :target: https://travis-ci.org/deviousops/robotframework-radius

Introduction
------------
`RadiusLibrary` is a test library for Robot Framework, providing keywords for handling the RADIUS protocol.
The library supports the creation of RADIUS clients and servers, and supports authentication, accounting and change of authorization requests.

Usage
-----
.. code:: robotframework



    *** Settings ***
    Library     RadiusLibrary

    *** Test Cases ***
    Should Receive Access Accept
        Create Client    auth    %{RADIUS_SERVER}    %{RADIUS_AUTH_PORT}    %{RADIUS_SECRET}    %{RADIUS_DICTIONARY}
        Create Access Request
        Add Request attribute    User-Name    user
        Add Request attribute    User-Password    x
        Add Request attribute    Acct-Session-Id  1234
        Add Request attribute    NAS-IP-Address  127.0.1.1
        Send Request
        Receive Access Accept
        Response Should Contain Attribute    Framed-IP-Address    10.0.0.100
        Response Should Contain Attribute    Class    premium

    Wrong Password Should Receive Access Reject
        Create Client    auth    %{RADIUS_SERVER}    %{RADIUS_AUTH_PORT}    %{RADIUS_SECRET}    %{RADIUS_DICTIONARY}
        Create Access Request
        Add Request attribute    User-Name    user
        Add Request attribute    User-Password    wrong
        Add Request attribute    Acct-Session-Id  126
        Send Request
        Receive Access Reject
        Response Should Contain Attribute    Reply-Message    authentication failed

For more information see https://rawgit.com/deviousops/robotframework-radius/master/doc/RadiusLibrary.html.

Links
-----
- http://www.robotframework.org
- http://github.com/wichert/pyrad

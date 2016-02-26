****************************************
RadiusLibrary
****************************************

.. image:: https://travis-ci.org/deviousops/robotframework-radius.svg?branch=master
    :target: https://travis-ci.org/deviousops/robotframework-radius

Introduction
------------
`RadiusLibrary` is a test library for Robot Framework, providing keywords for handling the RADIUS protocol.
The library supports the creation of RADIUS clients and servers, and supports authentication, accounting and change of authorization requests.

Installation
------------
Using the PIP installer

.. code:: shell

    $ pip install robotframework-radius

Or after cloning this repository

.. code:: shell

    $ python setup.py install

Example
-------

.. code:: robotframework

    *** Settings ***
    Library           RadiusLibrary

    *** Test Cases ***
    Should Receive Access Accept
        Create Client    auth    %{SERVER}    %{AUTHPORT}    %{SECRET}    %{DICTIONARY}
        Create Access Request
        Add Request attribute    User-Name    user
        Add Request attribute    User-Password    x
        Add Request attribute    Acct-Session-Id    1234
        Add Request attribute    NAS-IP-Address    127.0.1.1
        Send Request
        Receive Access Accept
        Response Should Contain Attribute    Framed-IP-Address    10.0.0.100
        Response Should Contain Attribute    Class    premium

    Wrong Password Should Receive Access Reject
        Create Client    auth    %{SERVER}    %{AUTHPORT}    %{SECRET}    %{DICTIONARY}
        Create Access Request
        Add Request attribute    User-Name    user
        Add Request attribute    User-Password    wrong
        Add Request attribute    Acct-Session-Id    126
        Send Request
        Receive Access Reject
        Response Should Contain Attribute    Reply-Message    authentication failed

For more info, have a look at the keyword documentation: https://rawgit.com/deviousops/robotframework-radius/master/doc/RadiusLibrary.html.

Usage
-----
Save the example above to `auth.robot`, execute the following commands.

.. code:: shell

    $ export SERVER=127.0.0.1
    $ export AUTHPORT=1812
    $ export SECRET=secret
    $ export DICTIONARY=/usr/share/freeradius/dictionary.rfc2865
    $ robot auth.robot

Links
-----
- http://www.robotframework.org
- http://github.com/wichert/pyrad

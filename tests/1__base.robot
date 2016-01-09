*** Settings ***
Library           RadiusLibrary
Library           Collections
Library           DateTime

*** test cases ***
Request Response Requests Should Pass
    Create Client    auth    127.0.0.1    1812    bras1001    dictionary
    ${req}= 	Send Access Request    User-Name=mike

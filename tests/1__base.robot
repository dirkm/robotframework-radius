*** Settings ***
Test Setup        Setup Client And Server
Library           RadiusLibrary
Library           Collections
Library           DateTime

*** test cases ***
Request Response Requests Should Pass
    ${req_attr}=    Create Dictionary    User-Name=testuser
    ${client_req}=    Send Request    client    AccessRequest    ${req_attr}
    ${server_req}=    Receive Request    server    AccessRequest
    Should Contain Attribute    ${server_req}    User-Name
    Run Keyword And Expect Error    KeyError: 25    Should Contain Attribute    ${server_req}    Class
    Send Response    server    ${server_req}    AccessAccept
    Receive Response    client    AccessAccept

*** Keywords ***
Setup Client And Server
    Create Client    client    127.0.0.1    11812    mysecret    dictionary
    Create Server    server    127.0.0.1    11812    mysecret    dictionary

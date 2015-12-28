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
    Should Contain Attribute    ${server_req}    key=User-Name
    Should Contain Attribute    ${server_req}    ${1}
    Should Contain Attribute    ${server_req}    key=${1}
    Should Contain Attribute    ${server_req}    key=User-Name   val=testuser
    Run Keyword And Expect Error    *    Should Contain Attribute    ${server_req}    key=User-Name   val=wronguser
    Should Contain Attribute    ${server_req}    User-Name	val=testuser
    Send Response    server    ${server_req}    AccessAccept
    Receive Response    client    AccessAccept

*** Keywords ***
Setup Client And Server
    Create Client    client    127.0.0.1    11812    mysecret    raddict=dictionary
    Create Server    server    127.0.0.1    11812    secret=mysecret    raddict=dictionary

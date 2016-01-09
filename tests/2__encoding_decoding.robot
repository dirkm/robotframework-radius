*** Settings ***
Test Setup        Setup Client And Server
Library           RadiusLibrary
Library           Collections
Library           DateTime

*** test cases ***
Encoding And Decoding String attribute Values Should Pass
    ${dct}=    Create Dictionary    User-Name=user
    ${creq}=    Send Request    client    AccessRequest    ${dct}
    ${sreq}=    Receive Request    server    AccessRequest
    Should Contain attribute    ${sreq}    User-Name
    Should Contain attribute    ${sreq}    User-Name    user
    Should Contain attribute    ${sreq}    key=User-Name    val=user
    Run Keyword And Expect Error    *    Should Contain attribute    ${sreq}    key=User-Name    val=unkown

*** Keywords ***
Setup Client And Server
    Create Client    client    127.0.0.1    11812    mysecret    raddict=dictionary
    Create Server    server    127.0.0.1    11812    mysecret    raddict=dictionary

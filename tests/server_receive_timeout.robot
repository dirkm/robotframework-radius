*** Settings ***
Library		RadiusClientLibrary
Library		DateTime
Test Template	Server Receive Timeout
Test Setup	Start Radius Server

*** Test Cases ***
0.3 Second  0.3
0.4 Second  0.4
0.5 Second  0.5
1.0 Second  1.0
2.0 Second  2.0
5.0 Second  5.0

*** Keywords ***
Start Radius Server
	Create Server	server	127.0.0.1	11812	mysecret	dictionary
Server Receive Timeout
	[Arguments]    ${timeout}
	${start}=	Get Current Date
	Run Keyword And Expect Error		*	Receive Request		server			AccessAccept	${timeout}
	${end}=		Get Current Date
        ${delta}=	Subtract Date From Date		${end}	${start}
	Should Be Equal As Numbers 	${timeout}	${delta}	precision=1

*** Settings ***
Library		RadiusLibrary
Library		DateTime
Test Template	Client Receive Timeout

*** Test Cases ***
0.3 Second  0.3
0.4 Second  0.4
0.5 Second  0.5
1.0 Second  1.0
2.0 Second  2.0
5.0 Second  5.0

*** Keywords ***
Client Receive Timeout
	[Arguments]    ${timeout}
	Create Client	client	127.0.0.1	11812	mysecret	dictionary
	${start}=	Get Current Date
	Run Keyword And Expect Error		*	Receive Response		client			AccessAccept	${timeout}
	${end}=		Get Current Date
        ${delta}=	Subtract Date From Date		${end}	${start}
	Should Be Equal As Numbers 	${timeout}	${delta}	precision=1

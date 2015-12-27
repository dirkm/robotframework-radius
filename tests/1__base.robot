*** Settings ***
Library		RadiusClientLibrary
Library		Collections
Library		DateTime
Test Setup	Setup Client And Server

*** test cases ***
Request Response Requests Should Pass
	${req_attr}=			Create Dictionary	User-Name=testuser
	${client_req}=			Send Request		client			AccessRequest		${req_attr}
	${server_req}=			Receive Request		server			AccessRequest
        Attribute Exists	${server_req}	User-Name
        Run Keyword And Expect Error	KeyError: 25	Attribute Exists	${server_req}	Class

	Send Response			server	${server_req}	AccessAccept
	Receive Response	client			AccessAccept

*** Keywords ***
Setup Client And Server
	Create Client	client	127.0.0.1	11812	mysecret	dictionary
	Create Server	server	127.0.0.1	11812	mysecret	dictionary

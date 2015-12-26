*** Settings ***
Library		RadiusClientLibrary
Library		DateTime
Test Setup	Setup Client And Server

*** test cases ***
Authorization Requests
	${req_attr}=			Create Dictionary	User-Name=testuser
	${client_req}=			Send Request		client			AccessRequest		${req_attr}
	${server_req}=			Receive Request		server			AccessRequest
	Send Response			server	${server_req}	AccessAccept

*** Keywords ***
Setup Client And Server
	Create Client	client	127.0.0.1	11812	mysecret	dictionary
	Create Server	server	127.0.0.1	11812	mysecret	dictionary

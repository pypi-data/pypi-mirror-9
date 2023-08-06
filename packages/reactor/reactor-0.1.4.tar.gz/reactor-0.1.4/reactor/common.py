# coding: utf8

import requests
import json

import reactor

headers = {'content-type': 'application/json'}

def _request(data):
	# print id(reactor), reactor.APPLICATION_ID, id(reactor.APPLICATION_ID)
	data['data'].update({'application_id': reactor.APPLICATION_ID})
	return requests.post(
		reactor.REACTOR_URL,
		headers=headers,
		data=json.dumps(data, sort_keys=reactor.JSON_SORT_KEYS)
	)

def collect(data):
	return _request({		
		'type': 'collect',
		'data': data
	})

def event(event_name, data):
	# this could overwrite users data
	data.update({'type': event_name})
	return _request({
		'type': 'event',
		'data': data,
	})
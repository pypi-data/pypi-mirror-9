# coding: utf8

import unittest2
import requests
import json
from copy import copy
from mock import Mock, call

import reactor

reactor.APPLICATION_ID = 'app_id_hash'
reactor.JSON_SORT_KEYS = True


class MainTests(unittest2.TestCase):
	_post_backup = None

	@classmethod
	def setUpClass(cls):
		post_mock = Mock()
		cls._post_backup = requests.post
		requests.post = post_mock

	@classmethod
	def tearDownClass(cls):
		requests.post = cls._post_backup

	def test_collect(self):
		data = {
			"session": 1405587905,
			"user_id": "661787707",
			"first_name_s": "John",
			"last_name_s": "Doe",
			"profile_picture_s": "https://s3.amazonaws.com/profiles.synopsi.tv/"
			"018c2044e968f9fe829d9cc54c45046d.jpeg_35_35.jpg",
			"registration_date_d": 1319707649,
			"gender_g": "male",
			"facebook_id_s": "1293033985",
			"email_s": "hello@reactor.am",
			"active_b": True,
			"geolocation_b": False,
			"share_facebook_b": False,
			"price_f": 10.20,
			'timezone_s': 'Europe/Bratislava'
		}

		data_sent = copy(data)
		response = reactor.collect(data)
		
		data_sent.update({'application_id': reactor.APPLICATION_ID})

		requests.post.assert_called_with(
			'https://api.reactor.am/collector/', 
			headers={'content-type': 'application/json'},
			data=json.dumps({
					'type': 'collect',
					'data': data_sent
				}, 
				sort_keys=True
			)
		)

	def test_event(self):
		data = {
			"user_id": "661787707",
			"name_s": "Gizmo",
			"price_f": 10.30
		}

		data_sent = copy(data)
		response = reactor.event('order', data)
		
		data_sent.update({
			'type': 'order',
			'application_id': reactor.APPLICATION_ID,
		})

		requests.post.assert_called_with(
			'https://api.reactor.am/collector/',
			headers={'content-type': 'application/json'},
			data=json.dumps({
					'type': 'event',
					'data': data_sent
				},
				sort_keys=True
			)
		)

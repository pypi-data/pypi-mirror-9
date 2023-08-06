"""
Tests for 'site' objects.

NOT YET IMPLEMENTED
"""

import json
import requests
import responses
import unittest


email = 'jathan@localhost'
BASE_URL = 'http://localhost:8990/api'
secret_key = 'MJMOl9W7jqQK3h-quiUR-cSUeuyDRhbn2ca5E31sH_I='


ADD_PAYLOAD_SUCCESS = {'name': 'Elvis', 'description': 'Presley'}
ADD_RESPOND_SUCCESS = {u'data': {u'site': {u'description': u'Presley', u'id': 2, u'name': u'Elvis'}}, u'status': u'ok'}
ADD_PAYLOAD_FAILURE = {'name': '', 'description': ''}
ADD_RESPOND_FAILURE = {u'error': {u'code': 400, u'message': u'Name is a required field.'}, u'status': u'error'}


class TestSites(unittest.TestCase):
    def setUp(self):
        self.base_url = BASE_URL + '/sites'
        self.content_type = 'application/json'
        self.headers = {'content-type': self.content_type}

    @responses.activate
    def test_add_success(self):
        """Test successful addition of a Site."""
        responses.add(
            responses.POST,
            self.base_url,
            body=json.dumps(ADD_RESPOND_SUCCESS),
            status=200,
            content_type=self.content_type
        )

        # Create the Site
        resp = requests.post(
            self.base_url,
            data=json.dumps(ADD_PAYLOAD_SUCCESS),
            headers=self.headers
        )

        # Verify success!
        self.assertEqual(resp.json(), ADD_RESPOND_SUCCESS)
        self.assertEqual(responses.calls[0].request.url, self.base_url)
        self.assertEqual(
            responses.calls[0].response.text,
            json.dumps(ADD_RESPOND_SUCCESS)
        )

    '''
    def test_add_failure():
        pass

    def test_list():
        pass

    def test_remove():
        pass

    def test_update():
        pass
    '''

import urllib2
import unittest

import mock
from generic_request_signer import client


class ClientTests(unittest.TestCase):

    sut_class = client.Client

    def setUp(self):
        self.api_credentials = FakeApiCredentials('/foo', '1', 'YQ==')
        self.sut = self.sut_class(self.api_credentials)
        self.urlopen_patch = mock.patch('urllib2.urlopen')
        self.urlopen = self.urlopen_patch.start()
        self.response_patch = mock.patch('generic_request_signer.response.Response')
        self.response = self.response_patch.start()

    def tearDown(self):
        self.urlopen_patch.stop()
        self.response_patch.stop()

    def test_init_captures_incoming_api_credentials(self):
        self.assertEqual(self.sut.api_credentials, self.api_credentials)

    def test_base_url_property_returns_api_credentials_base_url_value(self):
        self.assertEqual(self.sut._base_url, '/foo')

    def test_client_id_property_returns_api_credentials_client_id_value(self):
        self.assertEqual(self.sut._client_id, '1')

    def test_private_key_property_returns_api_credentials_private_key_value(self):
        self.assertEqual(self.sut._private_key, 'YQ==')

    def test_get_service_url_returns_valid_endpoint(self):
        self.assertEqual(self.sut._get_service_url('/bazz/'), '/foo/bazz/')

    def test_get_response_invokes_urlopen_with_request_return_value(self):
        with mock.patch.object(self.sut_class, '_get_request') as get_request:
            self.sut._get_response('GET', '/', {}, **{})
        self.urlopen.assert_called_once_with(get_request.return_value)

    def test_get_response_encodes_json_data_when_content_type_is_application_json(self):
        request_args = {"headers": {"Content-Type": "application/json"}}
        with mock.patch.object(self.sut_class, '_get_request') as get_request:
            self.sut._get_response('POST', '/endpoint', {'some': 'data'}, **request_args)
        get_request.assert_called_once_with('POST', '/endpoint', '{"some": "data"}', None, **request_args)

    def test_get_response_does_not_encode_json_data_when_json_content_already_a_string(self):
        request_args = {"headers": {"Content-Type": "application/json"}}
        json_data = '{"some": "data"}'
        with mock.patch.object(self.sut_class, '_get_request') as get_request:
            self.sut._get_response('POST', '/endpoint', json_data, **request_args)
        get_request.assert_called_once_with('POST', '/endpoint', json_data, None, **request_args)

    def test_get_response_invokes_get_request_incoming_params(self):
        method = 'GET'
        endpoint = '/'
        data = {'some': 'data'}
        kwargs = {'some': 'kwarg'}
        with mock.patch.object(self.sut_class, '_get_request') as get_request:
            self.sut._get_response(method, endpoint, data, **kwargs)
        get_request.assert_called_once_with(method, endpoint, data, None, **kwargs)

    def test_get_response_instantiates_response_with_urlopen_result(self):
        with mock.patch.object(self.sut_class, '_get_request'):
            self.sut._get_response('GET', '/', {}, **{})
        self.response.assert_called_once_with(self.urlopen.return_value)

    def test_when_urlopen_throws_exception_the_http_error_is_used_to_instantiate_the_response(self):
        http_error = urllib2.HTTPError('/', 500, '', None, None)
        self.urlopen.side_effect = http_error
        with mock.patch.object(self.sut_class, '_get_request'):
            self.sut._get_response('GET', '/', {}, **{})
        self.response.assert_called_once_with(http_error)

    def test_get_response_returns_urlopen_result_in_http_response_object(self):
        with mock.patch.object(self.sut_class, '_get_request'):
            result = self.sut._get_response('GET', '/', {}, **{})
        self.assertEqual(result, self.response.return_value)

    def test_get_request_instantiates_factory_with_params(self):
        with mock.patch('generic_request_signer.factory.SignedRequestFactory') as factory:
            self.sut._get_request('GET', '/', {}, **{})
        factory.assert_called_once_with('GET', '1', 'YQ==', {}, None)

    def test_get_request_instantiates_multipart_factory_with_params_when_files(self):
        with mock.patch('generic_request_signer.factory.MultipartSignedRequestFactory') as factory:
            self.sut._get_request('GET', '/', {}, files={'f': ('f', 'f')}, **{})
        factory.assert_called_once_with('GET', '1', 'YQ==', {}, {'f': ('f', 'f')})

    def test_get_request_invokes_create_request_on_factory(self):
        data = {'some': 'data'}
        with mock.patch('generic_request_signer.factory.SignedRequestFactory') as factory:
            self.sut._get_request('GET', '/endpoint/', data, **{})
        factory.return_value.create_request.assert_called_once_with('/foo/endpoint/')

    def test_get_request_returns_factory_create_request_value(self):
        with mock.patch('generic_request_signer.factory.SignedRequestFactory') as factory:
            result = self.sut._get_request('GET', '/', {}, **{})
        self.assertEqual(result, factory.return_value.create_request.return_value)


class FakeApiCredentials(object):

    def __init__(self, base_url, client_id, private_key):
        self.base_url = base_url
        self.client_id = client_id
        self.private_key = private_key

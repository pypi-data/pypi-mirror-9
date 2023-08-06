import datetime
import mock
import unittest
from collections import OrderedDict
from decimal import Decimal
from urllib import urlencode

from generic_request_signer import constants
from generic_request_signer.factory import SignedRequestFactory, json_encoding, default_encoding


class SignedRequestFactoryTests(unittest.TestCase):

    sut_class = SignedRequestFactory

    def setUp(self):
        self.method = 'GET'
        self.private_key = '1234'
        self.client_id = 'foobar'
        self.raw_data = {'some': 'data'}
        self.sut = self.sut_class(self.method, self.client_id, self.private_key, self.raw_data)

    def test_init_captures_incoming_client_id(self):
        self.assertEqual(self.sut.client_id, self.client_id)

    def test_init_captures_incoming_http_method(self):
        self.assertEqual(self.sut.http_method, self.method)

    def test_init_captures_incoming_private_key(self):
        self.assertEqual(self.sut.private_key, self.private_key)

    def test_init_captures_content_type_encodings(self):
        with mock.patch('generic_request_signer.factory.json_encoding') as json_encode:
            self.sut = self.sut_class(self.method, self.client_id, self.private_key, self.sut.raw_data)
        self.assertEqual(self.sut.content_type_encodings, {'application/json': json_encode})

    def test_json_encoding_dumps_json_data_verbatim(self):
        result = json_encoding("['foo', {'bar': ('baz', null, 1.0, 2)}]")
        self.assertEqual(result, "['foo', {'bar': ('baz', null, 1.0, 2)}]")

    def test_default_encoding_encodes_url_data(self):
        result = default_encoding({'foo': 'bar', 'baz': 'broken'})
        self.assertEqual(result, 'foo=bar&baz=broken')

    def test_build_signature_dict_for_content_type_generates_correct_python_dict_for_date_decimal_and_none_types(self):
        self.sut.raw_data = {'date': datetime.date(1900, 1, 2), "foo": Decimal(100.12), "empty": None}
        result = self.sut._build_signature_dict_for_content_type({"Content-Type": "application/json"})
        self.assertItemsEqual(result, {u"date": u"1900-01-02",
                                       u"foo": u"100.1200000000000045474735088646411895751953125",
                                       u"empty": None})

    @mock.patch('generic_request_signer.factory.default_encoding')
    def test_gets_encoder_when_data_and_method_does_not_use_querystring(self, default_encoding):
        headers = {'Content-Type': 'application/json'}
        self.sut.http_method = 'POST'
        with mock.patch.object(self.sut, 'content_type_encodings') as encodings:
            self.sut._get_data_payload(headers)
        encodings.get.assert_called_once_with('application/json', default_encoding)

    @mock.patch('generic_request_signer.factory.default_encoding')
    def test_encodes_data_when_data_and_method_does_not_use_querystring(self, default_encoding):
        headers = {'Content-Type': 'application/json'}
        self.sut.http_method = 'POST'
        with mock.patch.object(self.sut, 'content_type_encodings') as encodings:
            self.sut._get_data_payload(headers)
        encodings.get().assert_called_once_with(self.sut.raw_data)

    @mock.patch('generic_request_signer.factory.default_encoding')
    def test_get_data_payload_returns_encoding_func_when_raw_data_exists_and_not_get_request(self, default_encoding):
        headers = {'Content-Type': 'application/json'}
        self.sut.http_method = 'POST'
        with mock.patch.object(self.sut, 'content_type_encodings') as encodings:
            result = self.sut._get_data_payload(headers)
        self.assertEqual(result, encodings.get().return_value)

    @mock.patch('generic_request_signer.factory.default_encoding')
    def test_get_data_payload_does_not_invoke_get_on_internal_payload_when_no_raw_data_exists(self, default_encoding):
        self.sut.raw_data = None
        headers = {'Content-Type': 'application/json'}
        self.sut.http_method = 'POST'
        with mock.patch.object(self.sut, 'content_type_encodings') as encodings:
            self.sut._get_data_payload(headers)
        self.assertFalse(encodings.get.called)

    @mock.patch('generic_request_signer.factory.default_encoding')
    def test_get_data_payload_returns_none_when_no_raw_data_exists(self, default_encoding):
        self.sut.raw_data = None
        headers = {'Content-Type': 'application/json'}
        self.sut.http_method = 'POST'
        with mock.patch.object(self.sut, 'content_type_encodings'):
            result = self.sut._get_data_payload(headers)
        self.assertEqual(result, None)

    @mock.patch('generic_request_signer.factory.default_encoding')
    def test_get_data_payload_does_not_invoke_get_on_internal_payload_when_http_get(self, default_encoding):
        headers = {'Content-Type': 'application/json'}
        self.sut.http_method = 'GET'
        with mock.patch.object(self.sut, 'content_type_encodings') as encodings:
            self.sut._get_data_payload(headers)
        self.assertFalse(encodings.get.called)

    @mock.patch('generic_request_signer.factory.default_encoding')
    def test_get_data_payload_returns_none_when_http_get(self, default_encoding):
        headers = {'Content-Type': 'application/json'}
        self.sut.http_method = 'GET'
        with mock.patch.object(self.sut, 'content_type_encodings'):
            result = self.sut._get_data_payload(headers)
        self.assertEqual(result, None)

    def test_encodes_dict_of_data(self):
        result = default_encoding(OrderedDict((('a', 1), ('b', 2), ('c', 'asdf'))))
        self.assertEqual('a=1&b=2&c=asdf', result)

    def test_encodes_dict_with_nested_list(self):
        result = default_encoding(OrderedDict((('a', 1), ('b', [2, 4]), ('c', 'asdf'))))
        self.assertEqual('a=1&b=2&b=4&c=asdf', result)

    def test_encodes_dict_with_nested_empty_list(self):
        result = default_encoding(OrderedDict((('a', 1), ('b', []), ('c', 'asdf'))))
        self.assertEqual('a=1&c=asdf', result)

    @mock.patch('generic_request_signer.request.Request', mock.Mock)
    @mock.patch('generic_request_signer.factory.SignedRequestFactory._get_data_payload', mock.Mock)
    @mock.patch('generic_request_signer.factory.SignedRequestFactory.build_request_url')
    def test_create_request_invokes_build_request_url_with_params(self, build_url):
        url = '/foo/'
        self.sut.create_request(url)
        build_url.assert_called_once_with(url, {})

    @mock.patch('generic_request_signer.request.Request', mock.Mock)
    @mock.patch('generic_request_signer.factory.SignedRequestFactory.build_request_url', mock.Mock)
    @mock.patch('generic_request_signer.factory.SignedRequestFactory._get_data_payload')
    def test_create_request_invokes_get_data_payload_with_params(self, get_payload):
        kwargs = {'headers': 'foo'}
        self.sut.create_request('/foo/', **kwargs)
        get_payload.assert_called_once_with(kwargs.get('headers', {}))

    @mock.patch('generic_request_signer.request.Request')
    @mock.patch('generic_request_signer.factory.SignedRequestFactory._get_data_payload')
    @mock.patch('generic_request_signer.factory.SignedRequestFactory.build_request_url')
    def test_create_request_build_actual_request_object_with_params(self, build_url, get_payload, request):
        url = '/foo/'
        args = {'random': 'stuff'}
        kwargs = {'headers': 'foo'}
        self.sut.http_method = 'GET'
        self.sut.create_request(url, *args, **kwargs)
        request.assert_called_once_with('GET', build_url.return_value, get_payload.return_value, *args, **kwargs)

    @mock.patch('generic_request_signer.factory.SignedRequestFactory._get_data_payload', mock.Mock)
    @mock.patch('generic_request_signer.factory.SignedRequestFactory.build_request_url', mock.Mock)
    @mock.patch('generic_request_signer.request.Request')
    def test_create_request_returns_request_object(self, request):
        result = self.sut.create_request('/foo/', {})
        self.assertEqual(result, request.return_value)


class LegacySignedRequestFactoryTests(unittest.TestCase):

    def setUp(self):
        self.client_id = 'client_id'
        self.private_key = 'oVB_b3qrP3R6IDApALqehQzFy3DpMfob6Y4627WEK5A='
        self.raw_data = {'some': 'data'}
        self.sut = SignedRequestFactory('GET', self.client_id, self.private_key, self.raw_data)

    def test_sets_client_id_in_init(self):
        self.assertEqual(self.client_id, self.sut.client_id)

    def test_sets_private_key_in_init(self):
        self.assertEqual(self.private_key, self.sut.private_key)

    def test_adds_client_id_to_url(self):
        url = 'http://example.com/my/url'
        self.sut.raw_data = {}
        request = self.sut.create_request(url)

        querystring = "?{}={}".format(constants.CLIENT_ID_PARAM_NAME, self.client_id)
        querystring += "&{}={}".format(constants.SIGNATURE_PARAM_NAME, 'N1WOdyaBUVlPjKVyL3ionapOLAasFdvagfotfCdCW-Y=')
        self.assertEqual(url + querystring, request.get_full_url())

    def test_adds_signature_to_url(self):
        url = 'http://example.com/my/url'
        self.sut.raw_data = {}
        request = self.sut.create_request(url)

        querystring = "?{}={}".format(constants.CLIENT_ID_PARAM_NAME, self.client_id)
        querystring += "&{}={}".format(constants.SIGNATURE_PARAM_NAME, 'N1WOdyaBUVlPjKVyL3ionapOLAasFdvagfotfCdCW-Y=')
        self.assertEqual(url + querystring, request.get_full_url())

    @mock.patch('urllib2.Request.__init__')
    def test_urlencodes_data_as_part_of_url_when_method_is_get(self, urllib2_request):
        self.sut.raw_data = {'some': 'da ta', 'goes': 'he re'}
        self.sut.create_request('http://www.myurl.com')
        self.assertEqual(None, urllib2_request.call_args[0][1])
        url = "http://www.myurl.com?{}={}&some=da+ta&goes=he+re&{}={}".format(
            constants.CLIENT_ID_PARAM_NAME,
            self.client_id,
            constants.SIGNATURE_PARAM_NAME,
            'Npe9c-jKl2KhwGqvI8-DYxLQMqEm41swdGkQfQ9--lM='
        )
        self.assertEqual(url, urllib2_request.call_args[0][0])

    @mock.patch('urllib2.Request.__init__')
    def test_urlencodes_data_as_part_of_url_when_method_is_delete(self, urllib2_request):
        self.sut.http_method = 'DELETE'
        self.sut.raw_data = {'some': 'da ta', 'goes': 'he re'}
        self.sut.create_request('http://www.myurl.com')
        self.assertEqual(None, urllib2_request.call_args[0][1])
        url = "http://www.myurl.com?{}={}&some=da+ta&goes=he+re&{}={}".format(
            constants.CLIENT_ID_PARAM_NAME,
            self.client_id,
            constants.SIGNATURE_PARAM_NAME,
            'Npe9c-jKl2KhwGqvI8-DYxLQMqEm41swdGkQfQ9--lM='
        )
        self.assertEqual(url, urllib2_request.call_args[0][0])

    @mock.patch('urllib2.Request.__init__')
    def test_passes_data_to_urllib_request_when_method_is_not_get(self, urllib2_request):
        self.sut.raw_data = {'some': 'da ta', 'goes': 'he re'}
        self.sut.http_method = 'POST'
        self.sut.create_request('https://www.myurl.com')
        self.assertEqual(urlencode(self.sut.raw_data), urllib2_request.call_args[0][1])
        url = "https://www.myurl.com?{}={}&{}={}".format(
            constants.CLIENT_ID_PARAM_NAME,
            self.client_id,
            constants.SIGNATURE_PARAM_NAME,
            'cbseuxu6jVikia-u_Qxf5a4v3DKvyrkxjFSj4pnIHVw='
        )
        self.assertEqual(url, urllib2_request.call_args[0][0])

    def test_payload_is_empty_on_get_request_when_signed(self):
        url = "http://www.myurl.com?asdf=1234"
        self.sut.raw_data = {'asdf': '1234'}

        first_request = self.sut._build_signed_url(url, {})
        second_request = self.sut._build_signed_url(url, {})

        self.assertEqual(first_request, second_request)

    def test_get_data_payload_returns_none_when_no_raw_data(self):
        self.sut.raw_data = None
        payload_data = self.sut._get_data_payload({})
        self.assertEqual(None, payload_data)

    def test_get_data_payload_returns_none_when_get_request(self):
        self.sut.http_method = "GET"
        payload_data = self.sut._get_data_payload({})
        self.assertEqual(None, payload_data)

    def test_get_data_payload_returns_properly_encoded_data_when_content_type_header_present(self):
        self.sut.http_method = "POST"
        request_headers = {"Content-Type": "application/json"}
        payload_data = self.sut._get_data_payload(request_headers)
        self.assertEqual({'some': 'data'}, payload_data)

    def test_get_data_payload_returns_default_encoded_data_when_no_content_type_header(self):
        self.sut.http_method = "POST"
        payload_data = self.sut._get_data_payload(self.sut.raw_data)
        self.assertEqual('some=data', payload_data)

    def test_create_request_sends_header_data_to_get_data_payload(self):
        request_kwargs = {"headers": {"Content-Type": "application/json"}}
        with mock.patch.object(self.sut, "_get_data_payload") as get_payload:
            self.sut.create_request("http://google.com/", **request_kwargs)
        get_payload.assert_called_once_with(request_kwargs["headers"])

    def test_create_request_sends_empty_dict_to_get_data_payload_when_no_header(self):
        with mock.patch.object(self.sut, "_get_data_payload") as get_payload:
            self.sut.create_request("http://google.com/")
        get_payload.assert_called_once_with({})

    def test_input_files_property_will_wrap_single_file_in_list(self):
        files = {'file': ('name', 'file data')}
        self.sut.files = files
        self.assertEqual([files], self.sut.input_files)

    def test_input_files_property_will_not_wrap_list_of_files_in_list(self):
        files = [{'file': ('name', 'file data')}]
        self.sut.files = files
        self.assertEqual(files, self.sut.input_files)

    def test_will_flatten_nested_list_on_querystring_for_get_requests(self):
        self.sut.raw_data = {'items': ['a', 'b', 'c', 'd']}
        url = 'http://bit.ly/'
        self.sut.http_method = 'GET'
        self.sut.client_id = 'foobar'
        result = self.sut.build_request_url(url, {})
        self.assertIn('&items=a&items=b&items=c&items=d', result)


class SignedRequestFactoryBuildSignedUrlTests(unittest.TestCase):

    sut_class = SignedRequestFactory

    def setUp(self):
        self.method = 'GET'
        self.private_key = '1234'
        self.client_id = 'foobar'
        self.raw_data = {'some': 'data'}
        self.sut = self.sut_class(self.method, self.client_id, self.private_key, self.raw_data)

    def test_get_request_returns_url_with_data_client_id_and_signature(self):
        self.sut.raw_data = {'username': u'some.user', 'token': u'813bc1ad91dfadsfsdfsd02c'}
        url = 'http://bit.ly/'
        self.sut.http_method = 'GET'
        self.sut.client_id = 'foobar'
        result = self.sut.build_request_url(url, {})
        url = ''.join([
            'http://bit.ly/',
            '?__client_id=foobar',
            '&username=some.user',
            '&token=813bc1ad91dfadsfsdfsd02c',
            '&__signature=xfK_-z48Wh4vsEG-NoSN3FzE-2gO82cQvvVKjuB4qHs='
        ])
        self.assertEqual(result, url)

    def test_get_request_returns_url_with_spaces_escaped(self):
        self.sut.raw_data = {'username': u'some.user', 'token': u'813bc1ad91dfadsfsdfsd02c'}
        url = 'http://bit.ly/policy_number/8G BAD/'
        self.sut.http_method = 'POST'
        self.sut.client_id = 'foobar'
        result = self.sut.build_request_url(url, {})
        expected_url = ''.join([
            'http://bit.ly/policy_number/8G%20BAD/',
            '?__client_id=foobar&__signature=QTdfsNOKDzB34VbCorxavB5slXStdImlDbw-yq7nYc8='
        ])
        self.assertEqual(result, expected_url)

    def test_post_request_returns_url_with_only_client_id_and_signature(self):
        self.sut.raw_data = {'username': u'some.user', 'token': u'813bc1ad91dfadsfsdfsd02c'}
        url = 'http://bit.ly/'
        self.sut.http_method = 'POST'
        self.sut.client_id = 'foobar'
        result = self.sut.build_request_url(url, {})
        expected_url = 'http://bit.ly/?__client_id=foobar&__signature=mZ9tW9jlsmJ78fYvjO06LBLiY0COSAeYMHgqPE0Tb7s='
        self.assertEqual(result, expected_url)

    @mock.patch('apysigner.get_signature')
    def test_get_request_without_raw_data_returns_url_without_querystring(self, get_signature):
        get_signature.return_value = 'zzz123'
        self.sut.raw_data = None
        url = 'http://bit.ly/'
        self.sut.http_method = 'GET'
        self.sut.client_id = 'foobar'
        result = self.sut.build_request_url(url, {})
        self.assertEqual(result, 'http://bit.ly/?__client_id=foobar&__signature=zzz123')

    @mock.patch('apysigner.get_signature')
    def test_get_signature_invoked_with_no_data_when_get_request_and_valid_data(self, get_signature):
        url = 'http://bit.ly/'
        self.sut.raw_data = {'some': 'data'}
        self.sut.http_method = 'GET'
        self.sut._build_signed_url(url, {})
        get_signature.assert_called_once_with(self.private_key, url, {})

    @mock.patch('apysigner.get_signature')
    def test_get_signature_invoked_with_data_when_get_request_but_invalid_data(self, get_signature):
        url = 'http://bit.ly/'
        self.sut.raw_data = None
        self.sut.http_method = 'GET'
        self.sut._build_signed_url(url, {})
        get_signature.assert_called_once_with(self.private_key, url, None)

    @mock.patch('apysigner.get_signature')
    def test_get_signature_invoked_with_raw_data_when_post_request(self, get_signature):
        url = 'http://bit.ly/'
        self.sut.http_method = 'POST'
        self.sut._build_signed_url(url, {})
        get_signature.assert_called_once_with(self.private_key, url, self.sut.raw_data)

    @mock.patch('apysigner.get_signature')
    def test_get_signature_invoked_with_raw_data_when_posted_as_form_urlencoded(self, get_signature):
        url = 'http://bit.ly/'
        self.sut.http_method = 'POST'
        self.sut.raw_data = {'date': datetime.date(1900, 1, 2)}
        self.sut._build_signed_url(url, {"Content-Type": "application/x-www-form-urlencoded"})
        get_signature.assert_called_once_with(self.private_key, url, {'date': datetime.date(1900, 1, 2)})

    @mock.patch('apysigner.get_signature')
    def test_get_signature_invoked_with_json_turned_dict_when_posted_as_application_json(self, get_signature):
        url = 'http://bit.ly/'
        self.sut.http_method = 'POST'
        self.sut.raw_data = '{"date": "1900-01-02"}'
        self.sut._build_signed_url(url, {"Content-Type": "application/json"})
        get_signature.assert_called_once_with(self.private_key, url, '{"date": "1900-01-02"}')

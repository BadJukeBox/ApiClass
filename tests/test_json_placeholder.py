import unittest
import pytest
from unittest.mock import patch
import requests

from src.json_placeholder import RequestApi, JsonPlaceholderModifier


class TestRequestApi(unittest.TestCase):
    def setUp(self):
        self.req_tst = RequestApi('test')

    def response(self, response_code, data):
        r = requests.Response()
        r.status_code = response_code

        def json_func():
            return data
        r.json = json_func
        return r

    @patch('src.json_placeholder.requests.get')
    def test_get(self, mock_response):
        mock_response.return_value = self.response(200, {'title': 'test_get1'})
        resp = self.req_tst.get('/posts/1')
        assert resp.status_code == 200
        assert resp.json()['title'] == 'test_get1'

        with pytest.raises(requests.HTTPError):
            mock_response.side_effect = requests.HTTPError()
            self.req_tst.get('/failedpath')

    @patch('src.json_placeholder.requests.post')
    def test_post(self, mock_response):
        mock_response.return_value = self.response(200, {'title': 'test_post1'})
        resp = self.req_tst.post('/posts/1')
        assert resp.status_code == 200
        assert resp.json()['title'] == 'test_post1'

        with pytest.raises(requests.HTTPError):
            mock_response.side_effect = requests.HTTPError()
            self.req_tst.post('/failedpath')

    @patch('src.json_placeholder.requests.put')
    def test_put(self, mock_response):
        mock_response.return_value = self.response(200, {'title': 'test_put1'})
        resp = self.req_tst.put('/posts/1')
        assert resp.status_code == 200
        assert resp.json()['title'] == 'test_put1'

        with pytest.raises(requests.HTTPError):
            mock_response.side_effect = requests.HTTPError()
            self.req_tst.put('/failedpath')

    @patch('src.json_placeholder.requests.patch')
    def test_patch(self, mock_response):
        mock_response.return_value = self.response(200, {'title': 'test_patch1'})
        resp = self.req_tst.patch('/posts/1')
        assert resp.status_code == 200
        assert resp.json()['title'] == 'test_patch1'

        with pytest.raises(requests.HTTPError):
            mock_response.side_effect = requests.HTTPError()
            self.req_tst.patch('/failedpath')

    @patch('src.json_placeholder.requests.delete')
    def test_delete(self, mock_response):
        mock_response.return_value = self.response(200, {'title': 'test_delete1'})
        resp = self.req_tst.delete('/posts/1')
        assert resp.status_code == 200
        assert resp.json()['title'] == 'test_delete1'

        with pytest.raises(requests.HTTPError):
            mock_response.side_effect = requests.HTTPError()
            self.req_tst.delete('/failedpath')


class TestJsonPlaceholderModifier(unittest.TestCase):
    def setUp(self):
        self.json_mod_tst = JsonPlaceholderModifier()

    def response(self, response_code, data):
        r = requests.Response()
        r.status_code = response_code

        def json_func():
            return data
        r.json = json_func
        return r

    @patch('src.json_placeholder.RequestApi.get')
    def test_get_post_field(self, mock_get_post):
        mock_get_post.return_value = self.response(
            200,
            {
                'userId': 1,
                'id': 1,
                'title': 'test_title',
                'body': 'test_body'
            }
        )
        assert self.json_mod_tst.get_post_field('1', 'title') == 'test_title'
        assert not self.json_mod_tst.get_post_field('1', 'titles')

        mock_get_post.side_effect = requests.HTTPError()
        assert not self.json_mod_tst.get_post_field('1', 'title')

    @patch('src.json_placeholder.RequestApi.get')
    def test_insert_new_field(self, mock_get_post):
        mock_get_post.return_value = self.response(
            200,
            {
                'userId': 1,
                'id': 1,
                'title': 'test_title',
                'body': 'test_body'
            }
        )

        resp = self.json_mod_tst.insert_new_field('1', 'new_field', 'new_value')
        assert resp == {
                'userId': 1,
                'id': 1,
                'title': 'test_title',
                'body': 'test_body',
                'new_field': 'new_value'
            }

        mock_get_post.side_effect = requests.HTTPError()
        assert not self.json_mod_tst.insert_new_field('1', 'new_field', 'new_value')

    @patch('src.json_placeholder.RequestApi.post')
    def test_create_new_post(self, mock_post):
        test_body = {
            'userId': 102,
            'id': 102,
            'title': 'test_title102',
            'body': 'test_body102',
        }
        mock_post.return_value = self.response(200, test_body)
        assert self.json_mod_tst.create_new_post(test_body).json() == test_body

        mock_post.side_effect = requests.HTTPError()
        assert not self.json_mod_tst.create_new_post({})

    @patch('src.json_placeholder.RequestApi.delete')
    def test_delete_post(self, mock_delete):
        mock_delete.return_value = self.response(200, {})
        assert not self.json_mod_tst.delete_post('1').json()

        mock_delete.side_effect = requests.HTTPError()
        assert not self.json_mod_tst.delete_post('1')

import requests
import time
from datetime import datetime, timezone
import logging
from pprint import pprint

logger = logging.getLogger(__name__)


def retry(exception_list, total_tries=5, initial_wait=.5, backoff_factor=2, logger=None):
    def retry_decorator(func):
        def func_with_retry(*args, **kwargs):
            retries, delay = total_tries, initial_wait
            while retries > 0:
                try:
                    return func(*args, **kwargs)
                except exception_list as exception:
                    retries -= 1
                    if retries == 0:
                        logger.error(f'Function: {func.__name__} failed after {total_tries} attempts.\n')
                        raise
                    logger.warning(f'Function: {func.__name__} failed with exception: {exception}.\n'
                                   f'Retrying in {delay} seconds.\n')
                    time.sleep(delay)
                    delay *= backoff_factor

        return func_with_retry

    return retry_decorator


class RequestApi:
    def __init__(self, base_url: str):
        self.base_url = base_url

    @retry(Exception, total_tries=2, logger=logger)
    def get(self, api_path: str, payload: dict = None, headers: dict = None) -> requests.models.Response:
        response = requests.get(f'{self.base_url}{api_path}', json=payload, headers=headers)
        try:
            response.raise_for_status()
            return response
        except requests.HTTPError:
            raise

    @retry(Exception, total_tries=2, logger=logger)
    def get(self, api_path: str, payload: dict = None, headers: dict = None) -> requests.models.Response:
        response = requests.get(f'{self.base_url}{api_path}', json=payload, headers=headers)
        try:
            response.raise_for_status()
            return response
        except requests.HTTPError:
            raise

    @retry(Exception, total_tries=2, logger=logger)
    def post(self, api_path: str, payload: dict = None, headers: dict = None) -> requests.models.Response:
        response = requests.post(f'{self.base_url}{api_path}', json=payload, headers=headers)
        try:
            response.raise_for_status()
            return response
        except requests.HTTPError as e:
            print(e)

    @retry(Exception, total_tries=2, logger=logger)
    def put(self, api_path: str, payload: dict = None, headers: dict = None) -> requests.models.Response:
        response = requests.put(f'{self.base_url}{api_path}', json=payload, headers=headers)
        try:
            response.raise_for_status()
            return response
        except requests.HTTPError as e:
            print(e)

    @retry(Exception, total_tries=2, logger=logger)
    def patch(self, api_path: str, payload: dict = None, headers: dict = None) -> requests.models.Response:
        response = requests.patch(f'{self.base_url}{api_path}', json=payload, headers=headers)
        try:
            response.raise_for_status()
            return response
        except requests.HTTPError as e:
            print(e)

    @retry(Exception, total_tries=2, logger=logger)
    def delete(self, api_path: str, payload: dict = None, headers: dict = None) -> requests.models.Response:
        response = requests.delete(f'{self.base_url}{api_path}', json=payload, headers=headers)
        try:
            response.raise_for_status()
            return response
        except requests.HTTPError as e:
            print(e)


class JsonPlaceholderModifier:
    def __init__(self):
        self.requester = RequestApi('http://jsonplaceholder.typicode.com')

    def get_post_field(self, post_number: str, field: str) -> str:
        try:
            post = self.requester.get(f'/posts/{post_number}')
            return post.json()[field]
        except KeyError:
            logger.error(f'Error, field: {field} does not exist for post number: {post_number}.')
        except requests.HTTPError as err:
            logger.error(f'Error, {err}.')

    def insert_new_field(self, post_number: str, field_key: str, field_value: str) -> dict:
        try:
            post = self.requester.get(f'/posts/{post_number}').json()
        except requests.HTTPError as err:
            logger.error(f'Error, {err}.')
        else:
            post[field_key] = field_value
            return post

    def create_new_post(self, body: dict) -> requests.models.Response:
        try:
            return self.requester.post(
                '/posts',
                payload=body,
                headers={'Content-type': 'application/json; charset=UTF-8'}
            )
        except requests.HTTPError as err:
            logger.error(f'Error, {err}.')

    def delete_post(self, post_id: str) -> requests.models.Response:
        try:
            return self.requester.delete(f'/posts/{post_id}')
        except requests.HTTPError as err:
            logger.error(f'Error, {err}.')


if __name__ == '__main__':
    a = JsonPlaceholderModifier()

    print(a.get_post_field('99', 'title'))
    # print(a.get_post_field('101', 'title'))
    pprint(a.insert_new_field('100', 'time', datetime.now(timezone.utc).strftime("%m/%d/%Y, %H:%M:%S")))
    b = a.create_new_post({
        'title': 'Security Interview Post',
        'userId': 500,
        'body': 'This is an insertion test with a known API'
    })
    print((b.status_code, b.json()['id'], b.headers.get('x-powered-by')))
    c = a.delete_post('101')
    pprint((c.status_code, c.headers.get('x-content-type-options')))
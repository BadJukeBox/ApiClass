import requests
import time
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)


def retry(exception_list, total_tries=5, initial_wait=.5, backoff_factor=2, logger=None):
    """
    Allows for retry of a function. User can specify total tries, wait time, how quickly wait time increases.

    :param exception_list: (list<Exception) Which Exceptions user wants to handle as part of the retry logic.
    :param total_tries: (int) The total number of tries the retry decorator will attempt.
    :param initial_wait: (float) The time (in seconds) that the retry decorator will wait as a baseline before retrying.
    :param backoff_factor: (int) The speed at which the delay increases.
    :param logger: (logging.Logger) The logger that will record failures on retries and their error Types.
    :return:
    """
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
    """
    Basic request API class featuring retries on HTTPErrors (status codes >= 400). Takes a
    base API url and works off of paths for each request made. Supports GET/POST/PUT/PATCH/DELETE.

    All functions support the same arguments:
    :param api_path: (str) The path along the base URL that will be the endpoint hit.
    :param payload: (dict) The json payload or body for a request that needs it.
    :param headers: (dict) Any required headers for the request.
    :return: (requests.Response) The raw response with all fields on successful request.
    Logs error and returns None otherwise.
    """
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
    def post(self, api_path: str, payload: dict = None, headers: dict = None) -> requests.models.Response:
        response = requests.post(f'{self.base_url}{api_path}', json=payload, headers=headers)
        try:
            response.raise_for_status()
            return response
        except requests.HTTPError:
            raise

    @retry(Exception, total_tries=2, logger=logger)
    def put(self, api_path: str, payload: dict = None, headers: dict = None) -> requests.models.Response:
        response = requests.put(f'{self.base_url}{api_path}', json=payload, headers=headers)
        try:
            response.raise_for_status()
            return response
        except requests.HTTPError:
            raise

    @retry(Exception, total_tries=2, logger=logger)
    def patch(self, api_path: str, payload: dict = None, headers: dict = None) -> requests.models.Response:
        response = requests.patch(f'{self.base_url}{api_path}', json=payload, headers=headers)
        try:
            response.raise_for_status()
            return response
        except requests.HTTPError:
            raise

    @retry(Exception, total_tries=2, logger=logger)
    def delete(self, api_path: str, payload: dict = None, headers: dict = None) -> requests.models.Response:
        response = requests.delete(f'{self.base_url}{api_path}', json=payload, headers=headers)
        try:
            response.raise_for_status()
            return response
        except requests.HTTPError:
            raise


class JsonPlaceholderModifier:
    """
    JSONPlaceholder API Modifier. Can create/delete posts, and insert/find fields from these posts to show to the user.
    """
    def __init__(self):
        self.requester = RequestApi('http://jsonplaceholder.typicode.com')

    def get_post_field(self, post_number: str, field: str) -> str:
        """
        Get a specific field from a specific post.
        :param post_number: (str) The post number to find.
        :param field: (str) The field to find in said post.
        :return: Returns the field if found otherwise None.
        """
        try:
            post = self.requester.get(f'/posts/{post_number}')
            return post.json()[field]
        except KeyError:
            logger.error(f'Error, field: {field} does not exist for post number: {post_number}.')
        except requests.HTTPError as err:
            logger.error(f'Error, {err}.')

    def insert_new_field(self, post_number: str, field_key: str, field_value: str) -> dict:
        """
        Gets a specific post and adds a new field to it before returning it to the user.
        :param post_number: (str) The post number to find.
        :param field_key: (str) The field name to insert.
        :param field_value: (str) The field value to insert.
        :return: Returns the full post with the additional field, or None if there is an error.
        """
        try:
            post = self.requester.get(f'/posts/{post_number}').json()
        except requests.HTTPError as err:
            logger.error(f'Error, {err}.')
        else:
            post[field_key] = field_value
            return post

    def create_new_post(self, body: dict) -> requests.models.Response:
        """
        Creates a new post.
        :param body: (str) The body of the post to be created
        :return: The response from the action, or None on error.
        """
        try:
            return self.requester.post(
                '/posts',
                payload=body,
                headers={'Content-type': 'application/json; charset=UTF-8'}
            )
        except requests.HTTPError as err:
            logger.error(f'Error, {err}.')

    def delete_post(self, post_id: str) -> requests.models.Response:
        """
        Deletes a post.
        :param post_id: (str) the post id to delete.
        :return: The response from the action, or None on error.
        """
        try:
            return self.requester.delete(f'/posts/{post_id}')
        except requests.HTTPError as err:
            logger.error(f'Error, {err}.')


if __name__ == '__main__':
    a = JsonPlaceholderModifier()

    print(a.get_post_field('99', 'title'))
    print(a.insert_new_field('100', 'time', datetime.now(timezone.utc).strftime("%m/%d/%Y %H:%M:%S")))
    b = a.create_new_post({
        'title': 'Security Interview Post',
        'userId': 500,
        'body': 'This is an insertion test with a known API'
    })
    resp_tuple = (b.json()['id'], b.status_code, b.headers.get('x-powered-by'))
    print(f'id: {resp_tuple[0]}, resp_code: {resp_tuple[1]}, "x-Powered-By" header: {resp_tuple[2]}')
    c = a.delete_post('101')
    print((c.status_code, c.headers.get('x-content-type-options')))

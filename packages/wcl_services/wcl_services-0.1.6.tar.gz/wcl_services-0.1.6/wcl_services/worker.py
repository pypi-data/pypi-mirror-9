
"""
Experimental client for Western Cape Labs services APIs.

TODO:
 * Where do I start?
"""
from demands import HTTPServiceClient


class WorkerApiClient(object):

    """
    Client for WCL's Worker Task API.

    :param str auth_token:

        An access token. NOTE: This will be replaced by a proper
        authentication system at some point.

    :param str api_url:
        The full URL of the API. Defaults to
        ``https://worker.onelessthing.co.za/coreworker``.

    """

    def __init__(self, auth_token, api_url=None, session=None):
        self.auth_token = auth_token
        if api_url is None:
            api_url = "https://worker.onelessthing.co.za/coreworker"
        self.api_url = api_url
        self.headers = {'Authorization': 'Token ' + auth_token}
        if session is None:
            session = HTTPServiceClient(url=self.api_url,
                                         headers=self.headers,
                                         send_as_json=True)
        self.session = session

    def create_task(self, task):
        return self.session.post('/task/', data=task).json()

    def create_message(self, message):
        return self.session.post('/message/', data=message).json()

    def update_message(self, message_id, message):
        return self.session.put('/message/%s/' % message_id, data=message).json()

    def get_message(self, message_id):
        return self.session.get('/message/%s/' % message_id).json()

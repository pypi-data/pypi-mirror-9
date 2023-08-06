
"""
Experimental client for Western Cape Labs services APIs.

TODO:
 * Tests
"""
from demands import HTTPServiceClient


class AnalyticsApiClient(object):
    """
    Client for WCL's analytics API.

    :param str auth_token:

        An access token. NOTE: This will be replaced by a proper
        authentication system at some point.

    :param str api_url:
        The full URL of the API. Defaults to
        ``https://analytics.onelessthing.co.za/analytics``.

    """

    def __init__(self, auth_token, api_url=None, session=None):
        self.auth_token = auth_token
        if api_url is None:
            api_url = "https://analytics.onelessthing.co.za/analytics"
        self.api_url = api_url
        self.headers={'Authorization':'Token ' + auth_token}
        if session is None:
            session = HTTPServiceClient(url=self.api_url,
                                         headers=self.headers,
                                         send_as_json=True)
        self.session = session


    def log(self, event, data, uuid=None):
        payload = {
            "event": event,
            "data": data
        }
        # when UUID not present backend generates
        if uuid is not None:
            payload["uuid"] = uuid

        return self.session.post('/log/', data=payload).json()


    def backfill(self, event, data, at, uuid=None):
        """
        For entering historical data with an date time
        of something in the past
        """
        payload = {
            "event": event,
            "data": data,
            "at": at
        }
        # when UUID not present backend generates
        if uuid is not None:
            payload["uuid"] = uuid

        return self.session.post('/log/', data=payload).json()


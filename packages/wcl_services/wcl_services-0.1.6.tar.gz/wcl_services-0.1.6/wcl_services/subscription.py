
"""
Experimental client for Western Cape Labs services APIs.

TODO:
 * Tests
"""
from demands import HTTPServiceClient


class SubscriptionsApiClient(object):
    """
    Client for WCL's subscriptions API.

    :param str auth_token:

        An access token. NOTE: This will be replaced by a proper
        authentication system at some point.

    :param str api_url:
        The full URL of the API. Defaults to
        ``https://subscriptions.onelessthing.co.za/subscriptions``.

    """

    def __init__(self, auth_token, api_url=None, session=None):
        self.auth_token = auth_token
        if api_url is None:
            api_url = "https://subscriptions.onelessthing.co.za/subscriptions"
        self.api_url = api_url
        self.headers={
            'Authorization':'Token ' + auth_token,
            'Content-Type': 'application/json'
        }
        if session is None:
            session = HTTPServiceClient(url=self.api_url,
                                         headers=self.headers,
                                         send_as_json=True)
        self.session = session


    def create_subscription(self, subscription):
        return self.session.post('/subscriptions/', data=subscription).json()

    def update_subscription(self, subscription_id, subscription):   
        return self.session.put('/subscriptions/%s/' % subscription_id, data=subscription).json()

    def get_subscription(self, subscription_id):
        return self.session.get('/subscriptions/%s/' % subscription_id).json()

    def get_subscriptions(self):
        return self.session.get('/subscriptions/').json()

    def create_product(self, product):
        return self.session.post('/products/', data=product).json()

    def update_product(self, product_id, product):
        return self.session.put('/products/%s/' % product_id, data=product).json()

    def get_product(self, product_id):
        return self.session.get('/products/%s/' % product_id).json()

    def get_products(self):
        return self.session.get('/products/').json()

    def get_customers_subscriptions(self, customer_id):
        return self.session.get('/subscriptions/customer/%s' % customer_id).json()

    def get_subscriptions_by_status(self, status):
        return self.session.get('/subscriptions/?status__description=%s' % status).json()
        

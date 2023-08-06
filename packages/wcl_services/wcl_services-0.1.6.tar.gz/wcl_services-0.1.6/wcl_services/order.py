
"""
Experimental client for Western Cape Labs services APIs.

TODO:
 * Where do I start?
"""
from demands import HTTPServiceClient


class OrdersApiClient(object):

    """
    Client for WCL's orders API.

    :param str auth_token:

        An access token. NOTE: This will be replaced by a proper
        authentication system at some point.

    :param str api_url:
        The full URL of the API. Defaults to
        ``https://orders.onelessthing.co.za/orders``.

    """

    def __init__(self, auth_token, api_url=None, session=None):
        self.auth_token = auth_token
        if api_url is None:
            api_url = "https://orders.onelessthing.co.za/orders"
        self.api_url = api_url
        self.headers = {'Authorization': 'Token ' + auth_token}
        if session is None:
            session = HTTPServiceClient(url=self.api_url,
                                         headers=self.headers,
                                         send_as_json=True)
        self.session = session

    def create_order(self, order):
        return self.session.post('/orders/', data=order).json()

    def update_order(self, order_id, order):
        return self.session.put('/orders/%s/' % order_id, data=order).json()

    def get_order(self, order_id):
        return self.session.get('/orders/%s/' % order_id).json()

    def get_orders(self, params=None):
        return self.session.get('/orders/', params=params).json()

    def create_product(self, product):
        return self.session.post('/products/', data=product).json()

    def update_product(self, product_id, product):
        return self.session.put('/products/%s/' % product_id, data=product).json()

    def get_product(self, product_id):
        return self.session.get('/products/%s/' % product_id).json()

    def get_products(self, params=None):
        return self.session.get('/products/', params=params).json()

    def safe_get_product(self, product_id, default_product):
        response = self.session.get(
            '/products/%s/' % product_id,
            expected_response_codes=[404])
        return response.json() if response.is_ok else default_product

    def create_transaction(self, transaction):
        return self.session.post('/transactions/', data=transaction).json()

    def update_transaction(self, transaction_id, transaction):
        return self.session.put('/transactions/%s/' % transaction_id, data=transaction).json()

    def get_transaction(self, transaction_id):
        return self.session.get('/transactions/%s/' % transaction_id).json()

    def get_transactions(self, params=None):
        return self.session.get('/transactions/', params=params).json()

    def safe_get_transaction(self, transaction_id, default_transaction):
        response = self.session.get(
            '/transactions/%s/' % transaction_id,
            expected_response_codes=[404])
        return response.json() if response.is_ok else default_transaction

    def create_status(self, status):
        return self.session.post('/status/', data=status).json()

    def update_status(self, status_id, status):
        return self.session.put('/status/%s/' % status_id, data=status).json()

    def get_status(self, status_id):
        return self.session.get('/status/%s/' % status_id).json()

    def get_statuses(self, params=None):
        return self.session.get('/status/', params=params).json()

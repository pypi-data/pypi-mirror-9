
"""
Experimental client for Western Cape Labs services APIs.

TODO:
 * Tests
"""
from demands import HTTPServiceClient


class CustomersApiClient(object):
    """
    Client for WCL's customer API.

    :param str auth_token:

        An access token. NOTE: This will be replaced by a proper
        authentication system at some point.

    :param str api_url:
        The full URL of the API. Defaults to
        ``https://api.onelessthing.co.za/customers``.

    """

    def __init__(self, auth_token, api_url=None, session=None):
        self.auth_token = auth_token
        if api_url is None:
            api_url = "https://customers.onelessthing.co.za/customers"
        self.api_url = api_url
        self.headers={'Authorization':'Token ' + auth_token}
        if session is None:
            session = HTTPServiceClient(url=self.api_url,
                                         headers=self.headers,
                                         send_as_json=True)
        self.session = session


    def create_user(self, user):
        return self.session.post('/users/', data=user).json()

    def update_user(self, user_id, user):
        return self.session.put('/users/%s/' % user_id, data=user).json()

    def get_user(self, user_id):
        return self.session.get('/users/%s/' % user_id).json()

    def create_customer(self, customer):
        return self.session.post('/customers/', data=customer).json()

    def update_customer(self, customer_id, customer):
        return self.session.put('/customers/%s/' % customer_id, data=customer).json()

    def get_customer(self, customer_id):
        return self.session.get('/customers/%s/' % customer_id).json()

    def safe_get_customer(self, customer_id, default_customer):
        response = self.session.get(
            '/customers/%s/' % customer_id,
            expected_response_codes=[404])
        return response.json() if response.is_ok else default_customer

    def get_customers(self, include_inactive=False):
        if include_inactive:
            return self.session.get('/customers/').json()
        else:
            return self.session.get('/customers/active').json()

    def create_address(self, address):
        return self.session.post('/addresses/', data=address).json()

    def update_address(self, address_id, address):
        return self.session.put('/addresses/%s/' % address_id, data=address).json()

    def get_address(self, address_id):
        return self.session.get('/address/%s/' % address_id).json()

    def get_addresses(self, params=None):
        return self.session.get('/addresses/', params=params).json()

    def create_paymentmethod(self, paymentmethod):
        return self.session.post('/paymentmethods/', data=paymentmethod).json()

    def update_paymentmethod(self, paymentmethod_id, paymentmethod):
        return self.session.put('/paymentmethods/%s/' % paymentmethod_id,
            data=paymentmethod).json()

    def get_paymentmethod(self, paymentmethod_id):
        return self.session.get('/paymentmethods/%s/' % paymentmethod_id).json()

    def get_paymentmethods(self, params=None):
        return self.session.get('/paymentmethods/', params=params).json()


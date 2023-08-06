
"""
Experimental client for Western Cape Labs services APIs.

TODO:
 * Where do I start?
"""
from demands import HTTPServiceClient


class ProductsApiClient(object):

    """
    Client for WCL's products API.

    :param str auth_token:

        An access token. NOTE: This will be replaced by a proper
        authentication system at some point.

    :param str api_url:
        The full URL of the API. Defaults to
        ``https://products.onelessthing.co.za/products``.

    """

    def __init__(self, auth_token, api_url=None, session=None):
        self.auth_token = auth_token
        if api_url is None:
            api_url = "https://products.onelessthing.co.za/products"
        self.api_url = api_url
        self.headers = {'Authorization': 'Token ' + auth_token}
        if session is None:
            session = HTTPServiceClient(url=self.api_url,
                                         headers=self.headers,
                                         send_as_json=True)
        self.session = session

    def get_products(self, params=None):
        return self.session.get('/products/', params=params).json()

    def create_product(self, product):
        return self.session.post('/products/', data=product).json()

    def update_product(self, product_id, product):
        return self.session.put('/products/%s/' % product_id, data=product).json()

    def get_product(self, product_id):
        return self.session.get('/products/%s/' % product_id).json()

    def safe_get_product(self, product_id, default_product):
        response = self.session.get(
            '/products/%s/' % product_id,
            expected_response_codes=[404])
        return response.json() if response.is_ok else default_product

    def get_product_variants(self, product_id):
        return self.session.get('/products/%s/variants' % product_id).json()

    def create_variant(self, variant):
        return self.session.post('/variants/', data=variant).json()

    def update_variant(self, variant_id, variant):
        return self.session.put('/variants/%s/' % variant_id, data=variant).json()

    def get_variants(self, params=None):
        return self.session.get('/variants/', params=params).json()

    def get_variant(self, variant_id):
        return self.session.get('/variants/%s/' % variant_id).json()

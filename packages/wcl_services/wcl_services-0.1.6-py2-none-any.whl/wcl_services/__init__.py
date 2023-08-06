"""Western Cape Labs services client library."""

__version__ = "0.1.6"

from .customer import CustomersApiClient
from .product import ProductsApiClient
from .subscription import SubscriptionsApiClient
from .order import OrdersApiClient
from .analytic import AnalyticsApiClient
from .worker import WorkerApiClient

__all__ = [
    'CustomersApiClient', 'ProductsApiClient', 'SubscriptionsApiClient',
    'OrdersApiClient', 'AnalyticsApiClient', 'WorkerApiClient'
]

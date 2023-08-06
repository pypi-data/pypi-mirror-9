from __future__ import unicode_literals
from decimal import Decimal
import json
from unittest import TestCase

from . import CyberSourceProvider
from .. import PurchasedItem


CLIENT_ID = 'abc123'
PAYMENT_TOKEN = '5a4dae68-2715-4b1e-8bb2-2c2dbe9255f6'
SECRET = '123abc'
VARIANT = 'wallet'


class Payment(object):

    id = 1
    description = 'payment'
    currency = 'AED'
    delivery = Decimal(10)
    status = 'waiting'
    tax = Decimal(10)
    token = PAYMENT_TOKEN
    total = Decimal(210)
    variant = VARIANT
    transaction_id = None

    billing_first_name = 'John'
    billing_last_name = 'Doe'
    billing_address_1 = 'Somewhere'
    billing_address_2 = 'Over the Rainbow'
    billing_city = 'Washington'
    billing_country_code = 'US'
    billing_country_area = 'District of Columbia'
    billing_postcode = '20505'
    billing_email = 'test@room-303.com'

    customer_ip_address = '82.196.81.11'

    def change_status(self, status):
        self.status = status

    def get_failure_url(self):
        return 'http://cancel.com'

    def get_process_url(self):
        return 'http://example.com'

    def get_purchased_items(self):
        return [
            PurchasedItem(
                name='foo', quantity=Decimal('10'), price=Decimal('20'),
                currency='AED', sku='bar')]

    def get_success_url(self):
        return 'http://success.com'


class TestCyberSourceProvider(TestCase):

    def test_purchase(self):
        payment = Payment()
        provider = CyberSourceProvider(
            payment,
            capture=False,
            merchant_id='NI_MAGRUDY_AED',
            password='2DROk7NEWI2nrjKzG5LGjm1kMeN955MhVXFezc/1wzMi6tTmQyuSyxVWZveMlqi3PAuqIST+q9JQ4882JDH8b6xVlkMUmXGXdu7I4kfBeNNitAHmi7Kd4U5z9NPmzXExt+suXMTVI8rctpLP/cAv3qGQZVZSeVLBm/LET8I7W9/yi6NwPJV4pslSCVoFy5xu/Cjppeeh6d5rrK7HFioV3GKt15opCNwd9J/RC+Iw/ixQJ2qnVD4ELKQbwTaamzEYxxYH2ob4RIudESeGNURIIMRtopDeaLk8PgwpGG7sHC33g58e1UMe9cDQv55iO+ONWCHCsgLXzuerN5E6WEVBLQ==')
        # provider.refund()
        form = provider.get_form({
            'expiration_0': '8',
            'expiration_1': '2014',
            'name': 'Tester',
            'number': '4111111111111111',
            'cvv2': '123'})
        form.clean()
        print form.errors
        print form.cleaned_data

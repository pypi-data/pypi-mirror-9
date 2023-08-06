from __future__ import unicode_literals
import json
from uuid import uuid4

from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.translation import ugettext_lazy as _

from . import factory

DEFAULT_PAYMENT_STATUS_CHOICES = (
    ('waiting', _('Waiting for confirmation')),
    ('preauth', _('Pre-authorized')),
    ('confirmed', _('Confirmed')),
    ('rejected', _('Rejected')),
    ('refunded', _('Refunded')),
    ('error', _('Error')),
    ('input', _('Input'))
)
PAYMENT_STATUS_CHOICES = getattr(settings, 'PAYMENT_STATUS_CHOICES',
                                 DEFAULT_PAYMENT_STATUS_CHOICES)

FRAUD_CHOICES = (
    ('unknown', _('Unknown')),
    ('accept', _('Passed')),
    ('reject', _('Rejected')),
    ('review', _('Review')))


class PaymentAttributeProxy(object):

    def __init__(self, payment):
        self._payment = payment
        super(PaymentAttributeProxy, self).__init__()

    def __getattr__(self, item):
        data = json.loads(self._payment.extra_data or '{}')
        return data[item]

    def __setattr__(self, key, value):
        if key == '_payment':
            return super(PaymentAttributeProxy, self).__setattr__(key, value)
        try:
            data = json.loads(self._payment.extra_data)
        except ValueError:
            data = {}
        data[key] = value
        self._payment.extra_data = json.dumps(data)


class BasePayment(models.Model):
    '''
    Represents a single transaction. Each instance has one or more PaymentItem.
    '''
    variant = models.CharField(max_length=255)
    #: Transaction status
    status = models.CharField(
        max_length=10, choices=PAYMENT_STATUS_CHOICES, default='waiting')
    fraud_status = models.CharField(
        _('fraud check'), max_length=10, choices=FRAUD_CHOICES,
        default='unknown')
    fraud_message = models.TextField(blank=True, default='')
    #: Creation date and time
    created = models.DateTimeField(auto_now_add=True)
    #: Date and time of last modification
    modified = models.DateTimeField(auto_now=True)
    #: Transaction ID (if applicable)
    transaction_id = models.CharField(max_length=255, blank=True)
    #: Currency code (may be provider-specific)
    currency = models.CharField(max_length=10)
    #: Total amount (gross)
    total = models.DecimalField(max_digits=9, decimal_places=2, default='0.0')
    delivery = models.DecimalField(
        max_digits=9, decimal_places=2, default='0.0')
    tax = models.DecimalField(max_digits=9, decimal_places=2, default='0.0')
    description = models.TextField(blank=True, default='')
    billing_first_name = models.CharField(max_length=256, blank=True)
    billing_last_name = models.CharField(max_length=256, blank=True)
    billing_address_1 = models.CharField(max_length=256, blank=True)
    billing_address_2 = models.CharField(max_length=256, blank=True)
    billing_city = models.CharField(max_length=256, blank=True)
    billing_postcode = models.CharField(max_length=256, blank=True)
    billing_country_code = models.CharField(max_length=2, blank=True)
    billing_country_area = models.CharField(max_length=256, blank=True)
    billing_email = models.EmailField(blank=True)
    customer_ip_address = models.IPAddressField(blank=True)
    extra_data = models.TextField(blank=True, default='')
    message = models.TextField(blank=True, default='')
    token = models.CharField(max_length=36, blank=True, default='')
    captured_amount = models.DecimalField(
        max_digits=9, decimal_places=2, default='0.0')

    class Meta:
        abstract = True

    def change_status(self, status, message=''):
        '''
        Updates the Payment status and sends the status_changed signal.
        '''
        from .signals import status_changed
        self.status = status
        self.message = message
        self.save()
        status_changed.send(sender=type(self), instance=self)

    def change_fraud_status(self, status, message='', commit=True):
        available_statuses = [choice[0] for choice in FRAUD_CHOICES]
        if status not in available_statuses:
            raise ValueError(
                'Status should be one of: %s' % ', '.join(available_statuses))
        self.fraud_status = status
        self.fraud_message = message
        if commit:
            self.save()

    def save(self, *args, **kwargs):
        if not self.token:
            for _i in range(100):
                token = str(uuid4())
                if not type(self).objects.filter(token=token).exists():
                    self.token = token
                    break
        return super(BasePayment, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.variant

    def get_form(self, data=None):
        provider = factory(self)
        return provider.get_form(data=data)

    def get_purchased_items(self):
        return []

    def get_failure_url(self):
        raise NotImplementedError()

    def get_success_url(self):
        raise NotImplementedError()

    def get_process_url(self):
        return reverse('process_payment', kwargs={'token': self.token})

    def capture(self, amount=None):
        if self.status != 'preauth':
            raise ValueError(
                'Only pre-authorized payments can be captured.')
        provider = factory(self)
        amount = provider.capture(amount)
        if amount:
            self.captured_amount = amount
            self.change_status('confirmed')

    def release(self):
        if self.status != 'preauth':
            raise ValueError(
                'Only pre-authorized payments can be released.')
        provider = factory(self)
        provider.release()
        self.change_status('refunded')

    def refund(self, amount=None):
        if self.status != 'confirmed':
            raise ValueError(
                'Only charged payments can be refunded.')
        if amount > self.captured_amount:
            raise ValueError(
                'Refund amount can not be greater then captured amount')
        provider = factory(self)
        amount = provider.refund(amount)
        self.captured_amount -= amount
        if self.captured_amount == 0 and self.status != 'refunded':
            self.change_status('refunded')
        self.save()

    @property
    def attrs(self):
        return PaymentAttributeProxy(self)

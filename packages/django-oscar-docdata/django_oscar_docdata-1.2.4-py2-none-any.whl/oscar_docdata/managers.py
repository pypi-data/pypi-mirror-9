from . import appsettings
from django.db import models
from django.db.models.query import QuerySet
import django


class DocdataOrderQuerySet(QuerySet):
    """
    Chainable methods
    """

    def current_merchant(self):
        """
        Only select the current docdata account.
        """
        return self.filter(merchant_name=appsettings.DOCDATA_MERCHANT_NAME)

    def for_reference(self, docdata_ref):
        """
        Find an order by the reference that create_payment() returns (the "order key")
        """
        return self.get(order_key=docdata_ref)

    def for_order(self, order_number):
        """
        Find an order by the Oscar order number.
        """
        return self.get(merchant_order_id=order_number)


class DocdataOrderManager(models.Manager):
    """
    Extra methods for the DocdataOrder model.
    """
    queryset_class = DocdataOrderQuerySet

    def get_queryset(self):
        return self.queryset_class(self.model, using=self._db)

    if django.VERSION < (1,6):
        # For Django 1.5
        def get_query_set(self):
            return self.queryset_class(self.model, using=self._db)

    def current_merchant(self):
        """
        Only select the current docdata account.
        """
        # using .all() so Django selects the proper get_queryset() method.
        return self.all().current_merchant()

    def for_reference(self, docdata_ref):
        """
        Find an order by the reference that create_payment() returns (the "order key")
        """
        return self.all().for_reference(docdata_ref)

    def for_order(self, order_number):
        """
        Find an order by the Oscar order number.
        """
        return self.all().for_order(order_number)

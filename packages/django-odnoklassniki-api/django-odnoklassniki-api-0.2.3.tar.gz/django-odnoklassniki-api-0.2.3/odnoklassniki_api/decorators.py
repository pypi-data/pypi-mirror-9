# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

from django.core.exceptions import ImproperlyConfigured
from django.db.models.query import QuerySet
from django.utils.functional import wraps

try:
    from django.db.transaction import atomic
except ImportError:
    from django.db.transaction import commit_on_success as atomic


def list_chunks_iterator(l, n):
    """ Yield successive n-sized chunks from l.
    """
    for i in xrange(0, len(l), n):
        yield l[i:i+n]


def opt_arguments(func):
    '''
    Meta-decorator for ablity use decorators with optional arguments
    from here http://www.ellipsix.net/blog/2010/08/more-python-voodoo-optional-argument-decorators.html
    '''
    def meta_wrapper(*args, **kwargs):
        if len(args) == 1 and callable(args[0]):
            # No arguments, this is the decorator
            # Set default values for the arguments
            return func(args[0])
        else:
            def meta_func(inner_func):
                return func(inner_func, *args, **kwargs)
            return meta_func
    return meta_wrapper


@opt_arguments
def fetch_all(func, return_all=None, always_all=False, pagination='anchor', has_more='has_more'):
    """
    Class method decorator for fetching all items. Add parameter `all=False` for decored method.
    If `all` is True, method runs as many times as it returns any results.
    Decorator receive parameters:
      * callback method `return_all`. It's called with the same parameters
        as decored method after all itmes are fetched.
      * `always_all` bool - return all instances in any case of argument `all`
        of decorated method
    Usage:

        @fetch_all(return_all=lambda self,instance,*a,**k: instance.items.all())
        def fetch_something(self, ..., *kwargs):
        ....
    """
    def wrapper(self, all=False, instances_all=None, *args, **kwargs):

        if len(args) > 0:
            raise ImproperlyConfigured("It's prohibited to use non-key arguments for method decorated with @fetch_all,"
                                       " method is %s.%s(), args=%s" % (self.__class__.__name__, func.__name__, args))

        response = {}
        instances = func(self, **kwargs)
        if len(instances) == 2 and isinstance(instances, tuple):
            instances, response = instances

        if always_all or all:
            if isinstance(instances, QuerySet):
                if instances_all is None:
                    instances_all = instances.none()
                instances_count = instances.count()
                if instances_count:
                    instances_all |= instances
            elif isinstance(instances, list):
                if instances_all is None:
                    instances_all = []
                instances_count = len(instances)
                instances_all += instances
            else:
                raise ValueError("Wrong type of response from func %s. It should be QuerySet or list, "
                                 "not a %s" % (func, type(instances)))

            # recursive pagination
            # print has_more, response.keys()
            if instances_count and (has_more in response and response[has_more]
                                    or has_more not in response and pagination in response):
                kwargs[pagination] = response.get(pagination)
                return wrapper(self, all=all, instances_all=instances_all, **kwargs)

            if return_all:
                kwargs['instances'] = instances_all
                return return_all(self, **kwargs)
            else:
                return instances_all
        else:
            return instances

    return wraps(func)(wrapper)


@opt_arguments
def fetch_only_expired(func, timeout_days, expiration_fieldname='fetched', ids_argument='ids'):
    """
    Class method decorator for fetching only expired items. Add parameter `only_expired=False` for decored method.
    If `only_expired` is True, method substitute argument `ids_argument` with new value, that consist only expired ids.
    Decorator receive parameters:
      * `timeout_days` int, number of day, after that instance is suppose to be expired.
      * `expiration_fieldname` string, name of datetime field, that indicate time of instance last fetching
      * `ids_argument` string, name of argument, that store list of ids.
    Usage:

        @fetch_only_expired(timeout_days=3)
        def fetch_something(self, ..., *kwargs):
        ....
    """
    def wrapper(self, only_expired=False, *args, **kwargs):

        if len(args) > 0:
            raise ValueError("It's prohibited to use non-key arguments for method decorated with @fetch_all, "
                             "method is %s.%s(), args=%s" % (self.__class__.__name__, func.__name__, args))

        if only_expired:
            ids = kwargs[ids_argument]
            expired_at = datetime.now() - timedelta(timeout_days)
            ids_non_expired = self.model.objects.filter(**{'%s__gte' % expiration_fieldname: expired_at,
                                                           'pk__in': ids}).values_list('pk', flat=True)
            kwargs[ids_argument] = list(set(ids).difference(set(ids_non_expired)))

            instances = None
            if len(kwargs[ids_argument]):
                instances = func(self, **kwargs)
            return renew_if_not_equal(self.model, instances, ids)

        return func(self, **kwargs)

    return wraps(func)(wrapper)


@opt_arguments
def fetch_by_chunks_of(func, items_limit, ids_argument='ids'):
    """
    Class method decorator for fetching ammount of items bigger than allowed at once.
    Decorator receive parameters:
      * `items_limit`. Max limit of allowned items to fetch at once
      * `ids_argument` string, name of argument, that store list of ids.
    Usage:

        @fetch_by_chunks_of(1000)
        def fetch_something(self, ..., *kwargs):
        ....
    """
    def wrapper(self, *args, **kwargs):

        if len(args) > 0:
            raise ValueError("It's prohibited to use non-key arguments for method decorated with @fetch_all, "
                             "method is %s.%s(), args=%s" % (self.__class__.__name__, func.__name__, args))

        ids = kwargs[ids_argument]
        if ids:
            kwargs_sliced = dict(kwargs)
            for chunk in list_chunks_iterator(ids, items_limit):
                kwargs_sliced[ids_argument] = chunk
                instances = func(self, **kwargs_sliced)

            return renew_if_not_equal(self.model, instances, ids)
        else:
            return func(self, **kwargs)

    return wraps(func)(wrapper)


def renew_if_not_equal(model, instances, ids):
    return instances if instances is not None and len(ids) == instances.count() else model.objects.filter(pk__in=ids)


def opt_generator(func):
    """
    Class method or function decorator makes able to call generator methods as usual methods.
    Usage:

        @method_decorator(opt_generator)
        def some_method(self, ...):
            ...
            for count in some_another_method():
                yield (count, total)

    It's possible to call this method 2 different ways:

        * instance.some_method() - it will return nothing
        * for count, total in instance.some_method(as_generator=True):
            print count, total
    """
    def wrapper(*args, **kwargs):
        as_generator = kwargs.pop('as_generator', False)
        result = func(*args, **kwargs)
        return result if as_generator else list(result)
    return wraps(func)(wrapper)

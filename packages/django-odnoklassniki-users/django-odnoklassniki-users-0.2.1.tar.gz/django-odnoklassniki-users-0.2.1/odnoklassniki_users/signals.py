from django.dispatch import receiver
from django.conf import settings
from django.dispatch.dispatcher import Signal

from .tasks import OdnoklassnikiUsersFetchUsers

users_to_fetch = Signal(providing_args=['ids'])

@receiver(users_to_fetch)
def fetch_users(ids, **kwargs):
    only_expired = getattr(settings, 'ODNOKLASSNIKI_USERS_FETCH_ONLY_EXPIRED_USERS', True)
    async = getattr(settings, 'ODNOKLASSNIKI_USERS_FETCH_USERS_ASYNC', False)

    params = dict(ids=ids, only_expired=only_expired)
    if async:
        OdnoklassnikiUsersFetchUsers.apply_async(kwargs=params)
    else:
        OdnoklassnikiUsersFetchUsers.apply(kwargs=params)

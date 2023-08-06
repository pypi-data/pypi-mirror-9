from celery.task import Task
from odnoklassniki_users.models import User


class OdnoklassnikiUsersFetchUsers(Task):
    def run(self, ids, only_expired, *args, **kwargs):
        return User.remote.fetch(ids=ids)  # , only_expired=only_expired)
